import datetime
import logging
import threading

logging.basicConfig(level=logging.INFO)

# Disable annoying Camunda worker logs
logging.getLogger('camunda').setLevel(logging.WARNING)

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
        webhook_url = "http://localhost:5678/webhook/04ced486-2466-431f-b1fd-ea604848459b"
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


# Topic: update-stock NOT IN USE
def handle_update_stock(task: ExternalTask) -> TaskResult:
    """
    Handles the 'update-stock' topic from Camunda.
    Updates the inventory stock for a given item in the backend.
    Args:
        task (ExternalTask): The Camunda external task containing variables.
    Returns:
        TaskResult: The result to send back to Camunda (complete or failure).
    """
    inventory_id = task.get_variable("inventory_id")
    current_stock = task.get_variable("current_stock")
    amount = task.get_variable("amount")
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
        webhook_url = "http://localhost:5678/webhook/d5de05e8-553c-4074-b5c7-498a949f33d3"
        response = requests.get(webhook_url, timeout=30)  # Change to GET

        if response.status_code == 200:
            carts = response.json()
            available = len(carts) > 0
            logging.info(f"[DEBUG] Carts: {carts}, Available: {available}")
            
            result = {
                "carts": carts,
                "available": available,
            }
            
            # If available, include the cart_id of the first cart for update-cart-status
            if available:
                result["cart_id"] = carts[0]["id"]
            
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

    logging_to_frontend("Bridge", "Creating cart with checklist items")

    # Create the cart with default data
    cart_data = {
        "status": "Prepared",
        "patientId": task.get_variable("patientId", "patient-123"),
        "operation": task.get_variable("operation", "Medication Dispensing"),
        "operationDate": task.get_variable("operationDate", "2025-12-15"),
        "anaesthesiaType": task.get_variable("anaesthesiaType", "General"),
        "roomNumber": task.get_variable("roomNumber", "OR-01"),
    }

    try:
        # Create the cart
        create_cart_response = requests.post(f"{BACKEND_API_URL}/carts", json=cart_data)
        if create_cart_response.status_code != 200:
            return task.failure(
                error_message=f"Failed to create cart ({create_cart_response.status_code})",
                error_details=create_cart_response.text,
                max_retries=0,
                retry_timeout=1000,
            )

        cart = create_cart_response.json()
        cart_id = cart["id"]

        # Add checklist items as cart items (only if checked: true)
        for item in checklist:
            if not item.get("checked", False):
                continue  # Skip unchecked items

            medication_id = item["medication_id"]
            amount = item["amount"]

            # Fetch inventory_id for the medication
            inventory_response = requests.get(f"{BACKEND_API_URL}/inventory/{medication_id}")
            if inventory_response.status_code != 200:
                logging.warning(f"Failed to fetch inventory for {medication_id}, skipping")
                continue

            inventory_list = inventory_response.json()
            if not inventory_list:
                logging.warning(f"No inventory found for {medication_id}, skipping")
                continue

            inventory_id = inventory_list[0]["id"]  # Use the first inventory item

            # Add to cart using the correct endpoint
            cart_item_data = {
                "cart_id": cart_id,
                "inventory_id": inventory_id,
                "medication_id": medication_id,
                "amount": amount,
            }

            add_item_response = requests.post(f"{BACKEND_API_URL}/cart-items/add", json=cart_item_data)
            if add_item_response.status_code != 200:
                logging.warning(f"Failed to add cart item for {medication_id}: {add_item_response.text}")
                # Continue with other items instead of failing the whole task

        return task.complete({"cart_id": cart_id})

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
    cart_id = task.get_variable("cart_id")

    if not cart_id:
        return task.failure(
            error_message="cart_id is required",
            error_details="cart_id parameter is missing",
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
    worker = ExternalTaskWorker(worker_id="python-worker-" + str(i), base_url=BASE_URL)
    print(f"Listening for topic: {topic}")
    worker.subscribe(topic, handler)


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
