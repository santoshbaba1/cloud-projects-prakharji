import os

from google.cloud import firestore


def get_client() -> firestore.Client:
    project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")
    database = os.environ.get("FIRESTORE_DATABASE", "(default)")
    return firestore.Client(project=project_id, database=database)


def seed_carts(client: firestore.Client) -> None:
    carts = client.collection("carts")

    carts.document("cart_alice").set(
        {
            "customer_id": "alice@meridianretail.example",
            "status": "active",
            "created_at": firestore.SERVER_TIMESTAMP,
            "updated_at": firestore.SERVER_TIMESTAMP,
            "items": [
                {"sku": "SKU-1001", "qty": 2, "price": 19.99},
                {"sku": "SKU-2044", "qty": 1, "price": 49.50},
            ],
        }
    )

    carts.document("cart_bob").set(
        {
            "customer_id": "bob@meridianretail.example",
            "status": "active",
            "created_at": firestore.SERVER_TIMESTAMP,
            "updated_at": firestore.SERVER_TIMESTAMP,
            "items": [
                {"sku": "SKU-3007", "qty": 3, "price": 8.25},
            ],
        }
    )


def read_cart(client: firestore.Client, cart_id: str) -> None:
    doc = client.collection("carts").document(cart_id).get()
    if not doc.exists:
        print(f"Cart {cart_id} not found")
        return

    data = doc.to_dict()
    print(f"\nCart {cart_id}:")
    print(f"  customer_id: {data['customer_id']}")
    print(f"  status: {data['status']}")
    print("  items:")
    for item in data["items"]:
        print(f"    - {item['sku']} x{item['qty']} @ ${item['price']}")


def query_active_carts(client: firestore.Client) -> None:
    query = client.collection("carts").where("status", "==", "active")
    print("\nActive carts:")
    for doc in query.stream():
        data = doc.to_dict()
        print(f"  - {doc.id} ({data['customer_id']}, {len(data['items'])} item(s))")


def main() -> None:
    client = get_client()

    seed_carts(client)
    read_cart(client, "cart_alice")
    query_active_carts(client)


if __name__ == "__main__":
    main()
