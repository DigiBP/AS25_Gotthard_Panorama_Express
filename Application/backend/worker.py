import datetime
import json
import logging
import os
import threading

logging.basicConfig(level=logging.INFO)

# Disable annoying Camunda worker logs
#logging.getLogger('camunda').setLevel(logging.WARNING)

import requests
from camunda.external_task.external_task import ExternalTask, TaskResult
from camunda.external_task.external_task_worker import ExternalTaskWorker

# CONFIGURATION
# Camunda Engine
BASE_URL = "https://digibp.engine.martinlab.science/engine-rest"
# 2.  Backend
BACKEND_API_URL = "http://localhost:8000/api"

# POST to start the Process Process_1gnj26y
# url https://digibp.engine.martinlab.science/engine-rest/process-definition/key/Process_1gnj26y/tenant-id/mi25gotthard/start
# body {
#  "variables": {
#    "medication_id": {"value": "opioid-001", "type": "String"},
#    "medication_name": {"value": "fentanyl", "type": "String"},
#    "amount": {"value": 20, "type": "Integer"}
#  }
# }
# camunda username : mi25gotthard , password : password


def logging_to_frontend(event_type, msg):
    """
    Sends a workflow event notification to the frontend via the backend API and logs the event.
    Args:
        event_type (str): The type/category of the event.
        msg (str): The message to send and log.
    """
    response = requests.post(
        f"{BACKEND_API_URL}/notifications/workflow-event",
        json={"event_type": event_type, "message": msg},
    )
    logging.info(f"[{event_type}] {msg}")


def handle_inventory_check(task: ExternalTask) -> TaskResult:
    """
    Handles the 'inventory-check' topic from Camunda.
    Fetches inventory information for a given medication and returns stock details to Camunda.
    Args:
        task (ExternalTask): The Camunda external task containing variables.
    Returns:
        TaskResult: The result to send back to Camunda (complete or failure).
    """
    medication_id = task.get_variable("medication_id")  # e.g., "relaxant-001"
    amount_needed = task.get_variable("amount")

    logging_to_frontend(
        "Bridge", f"Fetching inventory for: {medication_id} (needed {amount_needed})"
    )

    try:

        response = requests.get(f"{BACKEND_API_URL}/inventory/{medication_id}")

        if response.status_code == 200:
            data = response.json()

            item = data[0] if isinstance(data, list) and data else data

            amount = item.get("amount", 0)
            min_stock = item.get("min_stock", 0)
            # Send variables back to Camunda
            logging_to_frontend(
                "Decision",
                f"{medication_id} going to the AI ? {amount - amount_needed < min_stock}",
            )
            return task.complete(
                {
                    "current_stock": amount,
                    "min_stock": min_stock,
                    "inventory_id": item.get("id"),
                }
            )
        else:
            return task.failure(
                error_message="Medication not found",
                error_details=f"API returned {response.status_code}",
                max_retries=0,
                retry_timeout=1000,
            )

    except Exception as e:
        return task.failure(
            error_message=str(e),
            error_details="Connection failed",
            max_retries=0,
            retry_timeout=1000,
        )


def handle_ai_check(task: ExternalTask) -> TaskResult:
    """
    Handles the 'ai-check' topic from Camunda.
    Checks with the AI/storage system for medication availability and location, updates the checklist, and returns results to Camunda.
    Args:
        task (ExternalTask): The Camunda external task containing variables.
    Returns:
        TaskResult: The result to send back to Camunda (complete or failure).
    """
    name = task.get_variable("medication_name")
    med_id = task.get_variable("medication_id")
    amount_needed = task.get_variable("amount")

    logging_to_frontend("Bridge", f"Asking AI/Storage about: {name}")

    try:
        # Send request to the specified webhook URL
        webhook_url = "http://localhost:5678/webhook/ea2b22f1-ce36-4988-8f59-f67b7ce05c6b"
        payload = {
            "medication_name": name,
            "medication_id": med_id,
            "amount": amount_needed
        }
        response = requests.post(webhook_url, json=payload)

        if response.status_code == 200:
            result_list = response.json()
            if isinstance(result_list, list) and result_list:
                output = result_list[0].get("output", {})
                found_str = output.get("found", "No")
                found = found_str.lower() == "yes"  # Convert string to boolean
                text = output.get("text", "")
                
                # Log the AI response text if present
                if text:
                    logging_to_frontend("AI Response", text)
                
                # Use defaults for missing fields
                location = "Unknown" # Not provided in response
                amount = amount_needed  # Not provided, use needed amount
                medication_id = med_id  # Not provided, use original

                # Instead of POST to /checklist, store in Camunda variable
                checklist_payload = [
                    {
                        "checked": found,
                        "name": name,
                        "location": location,
                        "amount": amount,
                        "medication_id": med_id,
                    }
                ]
                # No backend POST needed
                return task.complete(
                    {
                        "found": found,
                        "medication_id": medication_id,
                        "location": location,
                        "amount": amount,
                        "checklist": checklist_payload,  # Store as JSON variable
                    }
                )
            else:
                return task.failure(
                    error_message="Invalid response format from webhook",
                    error_details="Expected a non-empty list",
                    max_retries=0,
                    retry_timeout=1000,
                )
        else:
            return task.failure(
                error_message=f"Webhook request failed ({response.status_code})",
                error_details=response.text,
                max_retries=0,
                retry_timeout=1000,
            )

    except Exception as e:
        return task.failure(
            error_message=str(e),
            error_details="AI check request failed",
            max_retries=0,
            retry_timeout=1000,
        )


# Topic: update-stock
def handle_update_stock(task: ExternalTask) -> TaskResult:
    """
    Handles the 'update-stock' topic from Camunda.
    Updates the inventory stock for a given item in the backend.
    Args:
        task (ExternalTask): The Camunda external task containing variables.
    Returns:
        TaskResult: The result to send back to Camunda (complete or failure).
    """
    inventory_id_str = task.get_variable("inventory_id")
    current_stock = task.get_variable("current_stock")
    amount = task.get_variable("amount")
    
    # Convert string to integer since Camunda stores variables as strings
    # Handle various string formats that Camunda might use
    try:
        if isinstance(inventory_id_str, int):
            inventory_id = inventory_id_str
        elif isinstance(inventory_id_str, str):
            # Remove surrounding quotes if present (handles "\"9\"" -> "9")
            cleaned_str = inventory_id_str.strip('"')
            # Try to parse as JSON first (handles "9" -> 9)
            try:
                import json
                parsed = json.loads(cleaned_str)
                if isinstance(parsed, int):
                    inventory_id = parsed
                else:
                    inventory_id = int(parsed)
            except (json.JSONDecodeError, TypeError, ValueError):
                # If not JSON, try direct conversion
                inventory_id = int(cleaned_str)
        else:
            inventory_id = int(inventory_id_str)
    except (ValueError, TypeError) as e:
        return task.failure(
            error_message="Invalid inventory_id format",
            error_details=f"inventory_id must be a valid integer, got: {inventory_id_str} (type: {type(inventory_id_str)}), error: {e}",
            max_retries=0,
            retry_timeout=1000,
        )
    
    new_amount = current_stock - amount

    logging.info(f"[Bridge] Updating Inventory ID {inventory_id} to {new_amount}")
    logging_to_frontend(
        "[Bridge]", f"Updating Inventory ID {inventory_id} to {new_amount}"
    )

    try:
        response = requests.patch(
            f"{BACKEND_API_URL}/inventory/{inventory_id}",
            json={"new_amount": new_amount},
        )

        if response.status_code == 200:
            return task.complete()
        else:
            return task.failure(
                error_message=f"Update Failed ({response.status_code})",
                error_details=response.text,
                max_retries=0,
                retry_timeout=1000,
            )

    except Exception as e:
        return task.failure(
            error_message=str(e),
            error_details="Inventory update request failed",
            max_retries=0,
            retry_timeout=1000,
        )


def handle_create_order(task: ExternalTask) -> TaskResult:
    """
    Handles the 'create-order' topic from Camunda.
    Creates an order in the backend using variables from the Camunda process.
    Args:
        task (ExternalTask): The Camunda external task containing variables.
    Returns:
        TaskResult: The result to send back to Camunda (complete or failure).
    """
    order_name = "Camunda Order"
    order_date = task.get_variable("order_date")

    if not order_date:
        order_date = datetime.datetime.now().strftime("%Y-%m-%d")

    med_id = task.get_variable("medication_id")
    amount = task.get_variable("amount")
    is_internal = bool(task.get_variable("is_internal"))
    is_rush = bool(task.get_variable("is_rush"))

    if not order_date:
        return task.failure(
            error_message="order_date is required",
            error_details="order_date parameter is missing",
            max_retries=0,
            retry_timeout=1000,
        )

    payload = {
        "name": order_name,
        "date": order_date,
        "medications": [{"medicationId": med_id, "amount": amount}],
        "isInternal": is_internal,
        "isRush": is_rush,
    }

    logging_to_frontend("Bridge", f"Creating order {order_name}")

    try:
        response = requests.post(f"{BACKEND_API_URL}/orders", json=payload)

        if response.status_code == 200:
            body = response.json()
            return task.complete({"order_id": body.get("id")})
        else:
            return task.failure(
                error_message=f"Order creation failed ({response.status_code})",
                error_details=response.text,
                max_retries=0,
                retry_timeout=1000,
            )

    except Exception as e:
        return task.failure(
            error_message=str(e),
            error_details="Order creation request failed",
            max_retries=0,
            retry_timeout=1000,
        )
    


def handle_update_checklist(task: ExternalTask) -> TaskResult:
    """
    Handles the 'update-checklist' topic from Camunda.
    Updates the 'found' (checked) status of a medication in the checklist after the AI step.
    Args:
        task (ExternalTask): The Camunda external task containing variables.
    Returns:
        TaskResult: The result to send back to Camunda (complete or failure).
    """
    medication_id = task.get_variable("medication_id")
    new_found = bool(task.get_variable("new_found"))
    checklist = task.get_variable("checklist")  # Get from Camunda variable

    logging_to_frontend("Bridge", f"Updating checklist for {medication_id} to found: {new_found}")

    if not checklist:
        return task.failure(
            error_message="Checklist not found",
            error_details="Checklist variable is missing",
            max_retries=0,
            retry_timeout=1000,
        )

    # Find and update the item
    item = next((i for i in checklist if i.get("medication_id") == medication_id), None)
    if item:
        item["checked"] = new_found
        return task.complete({"checklist": checklist})  # Return updated checklist
    else:
        return task.failure(
            error_message="Checklist item not found",
            error_details=f"No item for medication_id {medication_id}",
            max_retries=0,
            retry_timeout=1000,
        )



def handle_check_carts(task: ExternalTask) -> TaskResult:
    """
    Handles the 'check-carts' topic from Camunda.
    Fetches cart information from the webhook and determines availability.
    Args:
        task (ExternalTask): The Camunda external task containing variables.
    Returns:
        TaskResult: The result to send back to Camunda (complete or failure).
    """
    logging_to_frontend("Bridge", "Checking carts availability")

    try:
        # Send GET request to the webhook (since POST is not registered)
        webhook_url = "http://localhost:5678/webhook/8c450380-3c3a-4de5-a3e4-5d030687aa1f"
        response = requests.get(webhook_url, timeout=30)  # Change to GET

        if response.status_code == 200:
            carts = response.json()
            
            # Normalize to list if it's a single dict
            if isinstance(carts, dict):
                carts = [carts]
            elif not isinstance(carts, list):
                return task.failure(
                    error_message="Invalid carts response format",
                    error_details="Expected list or dict",
                    max_retries=0,
                    retry_timeout=1000,
                )
            
            # Filter for carts with status "Prepared"
            prepared_carts = [cart for cart in carts if cart.get("status") == "Prepared"]
            available = len(prepared_carts) > 0
            logging.info(f"[DEBUG] Carts: {carts}, Prepared Carts: {prepared_carts}, Available: {available}")
            
            result = {
                "carts": carts,  # Return all carts for reference
                "available": available,
            }
            
            # If available, include the cart_id of the first prepared cart
            if available:
                result["cart_id"] = prepared_carts[0]["id"]
            
            return task.complete(result)
        else:
            return task.failure(
                error_message=f"Failed to fetch carts ({response.status_code})",
                error_details=response.text,
                max_retries=0,
                retry_timeout=1000,
            )

    except Exception as e:
        return task.failure(
            error_message=str(e),
            error_details="Carts check request failed",
            max_retries=0,
            retry_timeout=1000,
        )


def handle_create_cart(task: ExternalTask) -> TaskResult:
    """
    Handles the 'create-cart' topic from Camunda.
    Creates a new cart and adds checklist items as cart items using existing endpoints.
    Args:
        task (ExternalTask): The Camunda external task containing variables.
    Returns:
        TaskResult: The result to send back to Camunda (complete or failure).
    """
    checklist = task.get_variable("checklist")  # Get from Camunda variable

    if not checklist:
        return task.failure(
            error_message="Checklist not found",
            error_details="Checklist variable is missing",
            max_retries=0,
            retry_timeout=1000,
        )

        logging_to_frontend("Bridge", f"Creating cart with {len(default_cart_items)} medications from template")

    # Create the cart with default data, ensuring fallbacks for None
    cart_data = {
        "status": "In-Use",
        "patientId": task.get_variable("patientId") or "Unclaimed",
        "operation": task.get_variable("operation") or "Undefined",
        "operationDate": task.get_variable("operationDate") or "2025-12-15",
        "anaesthesiaType": task.get_variable("anaesthesiaType") or "General",
        "roomNumber": task.get_variable("roomNumber") or "Undefined",
    }

    try:
        # Create the cart
        create_cart_response = requests.post(f"{BACKEND_API_URL}/carts", json=cart_data)
        if create_cart_response.status_code != 200:
            return task.failure(
                error_message=f"Cart creation failed ({create_cart_response.status_code})",
                error_details=create_cart_response.text,
                max_retries=0,
                retry_timeout=1000,
            )
        
        cart = create_cart_response.json()
        logging.info(f"[DEBUG] Created cart: {cart}")
        
        # Helper function to get inventory_id for a medication
        def get_inventory_id(medication_id, required_amount=1):
            try:
                response = requests.get(f"{BACKEND_API_URL}/inventory/{medication_id}")
                if response.status_code == 200:
                    inventories = response.json()
                    # Find an inventory item with sufficient stock
                    for inv in inventories:
                        if inv.get("amount", 0) >= required_amount:
                            return inv["id"]
                    # If no inventory has enough stock, return the first one (or None)
                    return inventories[0]["id"] if inventories else None
                else:
                    logging.warning(f"Failed to get inventory for {medication_id}: {response.status_code}")
                    return None
            except Exception as e:
                logging.warning(f"Error getting inventory for {medication_id}: {e}")
                return None
        
        # Stock cart with default medications plus Camunda-requested medication
        default_cart_items = [
            {"medication_id": "local_anesthetic-001", "amount": 1.0, "time_sensitive": False},
            {"medication_id": "hypnotic-001", "amount": 1.0, "time_sensitive": True},
            {"medication_id": "opioid-001", "amount": 1.0, "time_sensitive": True},
            {"medication_id": "opioid-002", "amount": 1.0, "time_sensitive": True},
            {"medication_id": "vasoactive-002", "amount": 1.0, "time_sensitive": False},
            {"medication_id": "vasoactive-001", "amount": 1.0, "time_sensitive": False},
            {"medication_id": "analgetic-001", "amount": 1.0, "time_sensitive": False},
            {"medication_id": "antiemetic-001", "amount": 1.0, "time_sensitive": False},
            {"medication_id": "infusion-001", "amount": 1.0, "time_sensitive": False},
            {"medication_id": "infusion-003", "amount": 1.0, "time_sensitive": False}
        ]
        
        # Get Camunda variables (these should be set by the BPMN process)
        medication_id = task.get_variable("medication_id")
        amount_raw = task.get_variable("amount")
        
        # Validate required variables
        if not medication_id:
            return task.failure(
                error_message="medication_id is required",
                error_details="The BPMN process must set the medication_id variable",
                max_retries=0,
                retry_timeout=1000,
            )
        
        if amount_raw is None:
            return task.failure(
                error_message="amount is required", 
                error_details="The BPMN process must set the amount variable",
                max_retries=0,
                retry_timeout=1000,
            )
        
        # Convert amount to float, handling string conversion from Camunda
        try:
            if isinstance(amount_raw, str):
                # Handle JSON string format from Camunda
                import json
                try:
                    parsed = json.loads(amount_raw)
                    amount = float(parsed)
                except (json.JSONDecodeError, ValueError):
                    amount = float(amount_raw)
            else:
                amount = float(amount_raw)
        except (ValueError, TypeError):
            return task.failure(
                error_message="Invalid amount format",
                error_details=f"amount must be a valid number, got: {amount_raw}",
                max_retries=0,
                retry_timeout=1000,
            )
        
        # Debug logging for Camunda variables
        logging.info(f"[DEBUG] Camunda variables - medication_id: {medication_id}, amount_raw: {amount_raw}, amount_converted: {amount}")
        logging_to_frontend("Bridge", f"Creating cart with medication: {medication_id}, amount: {amount}")
        if medication_id:
            # Check if requested medication is already in defaults
            found = False
            for item in default_cart_items:
                if item["medication_id"] == medication_id:
                    # Update amount to the requested amount
                    item["amount"] = amount
                    found = True
                    logging.info(f"[DEBUG] Updated default {medication_id} amount to {amount}")
                    break
            
            # If not in defaults, add it
            if not found:
                default_cart_items.append({
                    "medication_id": medication_id,
                    "amount": amount,
                    "time_sensitive": False  # Default for requested medications
                })
                logging.info(f"[DEBUG] Added requested medication {medication_id} with amount {amount}")
        
        # Add all medications to cart using bulk API
        bulk_items = []
        for item in default_cart_items:
            inventory_id = get_inventory_id(item["medication_id"], item["amount"])
            if inventory_id:
                bulk_items.append({
                    "cart_id": cart["id"],
                    "inventory_id": inventory_id,
                    "medication_id": item["medication_id"],
                    "amount": item["amount"],
                    "time_sensitive": item["time_sensitive"]
                })
            else:
                logging.warning(f"No inventory found for {item['medication_id']}")
        
        if bulk_items:
            bulk_response = requests.post(
                f"{BACKEND_API_URL}/cart-items/add-bulk",
                json=bulk_items
            )
            if bulk_response.status_code == 200:
                added_items = bulk_response.json()
                logging.info(f"[DEBUG] Successfully added {len(added_items)}/{len(bulk_items)} medications to cart {cart['id']} in bulk")
                if len(added_items) < len(bulk_items):
                    logging.warning(f"[DEBUG] Partial success: {len(bulk_items) - len(added_items)} medications skipped due to insufficient inventory")
            else:
                logging.warning(f"Bulk add failed: {bulk_response.text}")
                # Fallback to individual adds if bulk fails
                added_count = 0
                skipped_count = 0
                for item_data in bulk_items:
                    add_response = requests.post(f"{BACKEND_API_URL}/cart-items/add", json=item_data)
                    if add_response.status_code == 200:
                        added_count += 1
                    else:
                        skipped_count += 1
                        logging.warning(f"Failed to add {item_data['medication_id']}: {add_response.text}")
                logging.info(f"[DEBUG] Fallback: added {added_count}/{len(bulk_items)} medications individually, {skipped_count} skipped")
        else:
            logging.warning("No medications could be added to cart (no inventory available)")
        
        # Return both cart object and cart_id for Camunda compatibility
        return task.complete({"cart": cart, "cart_id": cart["id"]})

    except Exception as e:
        return task.failure(
            error_message=str(e),
            error_details="Create cart request failed",
            max_retries=0,
            retry_timeout=1000,
        )


def handle_update_cart_status(task: ExternalTask) -> TaskResult:
    """
    Handles the 'update-cart-status' topic from Camunda.
    Updates the cart status to 'In-Use'.
    Args:
        task (ExternalTask): The Camunda external task containing variables.
    Returns:
        TaskResult: The result to send back to Camunda (complete or failure).
    """
    cart_id_str = task.get_variable("cart_id")

    if not cart_id_str:
        return task.failure(
            error_message="cart_id is required",
            error_details="cart_id parameter is missing",
            max_retries=0,
            retry_timeout=1000,
        )

    # Convert string to integer since Camunda stores variables as strings
    # Handle various string formats that Camunda might use
    try:
        if isinstance(cart_id_str, int):
            cart_id = cart_id_str
        elif isinstance(cart_id_str, str):
            # Remove surrounding quotes if present (handles "\"9\"" -> "9")
            cleaned_str = cart_id_str.strip('"')
            # Try to parse as JSON first (handles "9" -> 9)
            try:
                import json
                parsed = json.loads(cleaned_str)
                if isinstance(parsed, int):
                    cart_id = parsed
                else:
                    cart_id = int(parsed)
            except (json.JSONDecodeError, TypeError, ValueError):
                # If not JSON, try direct conversion
                cart_id = int(cleaned_str)
        else:
            cart_id = int(cart_id_str)
    except (ValueError, TypeError) as e:
        return task.failure(
            error_message="Invalid cart_id format",
            error_details=f"cart_id must be a valid integer, got: {cart_id_str} (type: {type(cart_id_str)}), error: {e}",
            max_retries=0,
            retry_timeout=1000,
        )

    logging_to_frontend("Bridge", f"Updating cart {cart_id} status to 'In-Use'")

    try:
        # Use the PATCH /status endpoint with the correct payload
        response = requests.patch(
            f"{BACKEND_API_URL}/carts/{cart_id}/status",
            json={"new_status": "In-Use"},  # Matches the embed=True body
        )

        if response.status_code == 200:
            return task.complete()
        else:
            return task.failure(
                error_message=f"Cart status update failed ({response.status_code})",
                error_details=response.text,
                max_retries=0,
                retry_timeout=1000,
            )

    except Exception as e:
        return task.failure(
            error_message=str(e),
            error_details="Cart status update request failed",
            max_retries=0,
            retry_timeout=1000,
        )


def start_subscription(topic, handler, i):
    """
    Starts a Camunda ExternalTaskWorker subscription for a given topic in a separate thread.
    Args:
        topic (str): The Camunda topic to subscribe to.
        handler (function): The handler function for the topic.
        i (int): Worker index for unique worker ID.
    """
    worker = ExternalTaskWorker(
        worker_id="python-worker-" + str(i), 
        base_url=BASE_URL,
        config={'tenantId': 'mi25gotthard'}  # Set tenant here
    )
    print(f"Listening for topic: {topic}")
    worker.subscribe(topic, handler)  # Remove tenant_id from subscribe


def start_camunda_workers():
    """
    Starts Camunda worker threads for all defined topics.
    Each topic is handled by a separate thread running its own ExternalTaskWorker.
    """
    topics = [
        ("ai-check", handle_ai_check),
        ("inventory-check", handle_inventory_check),
        ("update-stock", handle_update_stock),
        ("create-order", handle_create_order),
        ("update-checklist", handle_update_checklist),
        ("check-carts", handle_check_carts),
        ("create-cart", handle_create_cart),
        ("update-cart-status", handle_update_cart_status),  # Add new topic
    ]

    idx = 1
    for topic, handler in topics:
        # daemon=True means these threads will die automatically when Uvicorn shuts down
        t = threading.Thread(
            target=start_subscription, args=(topic, handler, idx), daemon=True
        )
        t.start()
        idx = idx + 1


if __name__ == "__main__":

    start_camunda_workers()