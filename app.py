import pymysql
import graphene
import os
from flask import Flask
from flask_graphql import GraphQLView

DB_CONFIG = {
    'host': os.getenv('DB_HOST'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_NAME'),
    'port': int(os.getenv('DB_PORT', 3306))
}

def get_db_connection():
    return pymysql.connect(**DB_CONFIG)

class User(graphene.ObjectType):
    user_id = graphene.Int()
    username = graphene.String()
    email = graphene.String()
    first_name = graphene.String()
    last_name = graphene.String()
    phone_number = graphene.String()
    address = graphene.String()
    created_at = graphene.String()

class Product(graphene.ObjectType):
    product_id = graphene.Int()
    product_name = graphene.String()
    price = graphene.Float()
    quantity = graphene.Int()
    description = graphene.String()
    image_url = graphene.String()
    is_sold = graphene.Boolean()
    created_at = graphene.String()
    seller_id = graphene.Int()

class Order(graphene.ObjectType):
    order_id = graphene.Int()
    quantity = graphene.Int()
    total_price = graphene.Float()
    purchase_time = graphene.String()
    status = graphene.String()
    seller_id = graphene.Int()
    buyer_id = graphene.Int()
    product_id = graphene.Int()
    created_at = graphene.String()

class CombinedData(graphene.ObjectType):
    order = graphene.Field(Order)
    product = graphene.Field(Product)
    seller = graphene.Field(User)
    buyer = graphene.Field(User)

class Query(graphene.ObjectType):
    combined_data = graphene.List(CombinedData, order_id=graphene.Int(required=False))

    def resolve_combined_data(self, info, order_id=None):
        query = """
        SELECT 
            o.*, 
            p.*, 
            s.user_id AS seller_user_id, s.username AS seller_username, s.email AS seller_email, 
            s.first_name AS seller_first_name, s.last_name AS seller_last_name, 
            s.phone_number AS seller_phone_number, s.address AS seller_address, 
            b.user_id AS buyer_user_id, b.username AS buyer_username, b.email AS buyer_email, 
            b.first_name AS buyer_first_name, b.last_name AS buyer_last_name, 
            b.phone_number AS buyer_phone_number, b.address AS buyer_address
        FROM Orders o
        JOIN Products p ON o.product_id = p.product_id
        JOIN Users s ON o.seller_id = s.user_id
        JOIN Users b ON o.buyer_id = b.user_id
        """
        if order_id:
            query += " WHERE o.order_id = %s"

        connection = get_db_connection()
        with connection.cursor() as cursor:
            cursor.execute(query, (order_id,) if order_id else None)
            results = cursor.fetchall()

        connection.close()

        combined_data = []
        for row in results:
            combined_data.append(
                CombinedData(
                    order=Order(
                        order_id=row[0],
                        quantity=row[1],
                        total_price=row[2],
                        purchase_time=row[3],
                        status=row[4],
                        seller_id=row[5],
                        buyer_id=row[6],
                        product_id=row[7],
                        created_at=row[8],
                    ),
                    product=Product(
                        product_id=row[9],
                        product_name=row[10],
                        price=row[11],
                        quantity=row[12],
                        description=row[13],
                        image_url=row[14],
                        is_sold=row[15],
                        created_at=row[16],
                        seller_id=row[17],
                    ),
                    seller=User(
                        user_id=row[18],
                        username=row[19],
                        email=row[20],
                        first_name=row[21],
                        last_name=row[22],
                        phone_number=row[23],
                        address=row[24],
                    ),
                    buyer=User(
                        user_id=row[25],
                        username=row[26],
                        email=row[27],
                        first_name=row[28],
                        last_name=row[29],
                        phone_number=row[30],
                        address=row[31],
                    ),
                )
            )
        return combined_data

schema = graphene.Schema(query=Query)

app = Flask(__name__)
app.add_url_rule(
    "/graphql", view_func=GraphQLView.as_view("graphql", schema=schema, graphiql=True)
)

if __name__ == "__main__":
    app.run(debug=True)
