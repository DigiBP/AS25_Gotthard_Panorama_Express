import datetime
import logging
import threading

logging.basicConfig(level=logging.INFO)

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


# TODO don't know the exact steps
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
        # get location
        response = requests.get(f"{BACKEND_API_URL}/inventory/{med_id}")

        if response.status_code == 200:
            result = response.json()[0]
            location = result.get("location") or "Unknown"
        else:
            location = "Unknown"

        payload = [
            {
                "checked": True,
                "name": name,
                "location": location,
                "amount": amount_needed,
            }
        ]

        response = requests.post(f"{BACKEND_API_URL}/checklist", json=payload)

        if response.status_code == 200:
            result = response.json()[0]
            found = result.get("checked")

            return task.complete(
                {
                    "found": found,
                    "medication_id": result.get("medication_id"),
                    "location": result.get("location"),
                    "amount": result.get("amount"),
                }
            )
        else:
            return task.failure(
                error_message=f"AI Check Failed ({response.status_code})",
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
