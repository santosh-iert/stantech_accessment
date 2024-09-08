import pandas as pd
from pydantic import BaseModel, ValidationError, constr
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from flask import Flask, request, jsonify
import bcrypt
from functools import wraps
import jwt
import datetime

# Creating the declarative base object for Database Operations
Base = declarative_base()


class Product(Base):
    """
    product class to define the products table
    """
    __tablename__ = 'products'
    product_id = Column(Integer, primary_key=True)
    product_name = Column(String(255))
    category = Column(String(255))
    price = Column(Float)
    quantity_sold = Column(Integer)
    rating = Column(Float)
    review_count = Column(Integer)


class User(Base):
    """
        Users class to defines the users table
    """
    __tablename__ = 'users'
    user_id = Column(Integer, primary_key=True)
    username = Column(String(255), unique=True)
    password_hash = Column(String(255))

# Function to create mysql database connection
def connect_db():
    """
    Function to make connection with mysql database
    Please overwrite the database credentials
    """
    # Change the following Database credentials for production this can be handled in .env file
    db_username = "<user_name>"
    db_password = "<password>"
    db_name = "<db_name>"
    db_host = "localhost"
    db_port = "3306"
    engine = create_engine(f"mysql+pymysql://{db_username}:{db_password}@{db_host}:{db_port}/{db_name}")
    Base.metadata.create_all(engine)
    return engine



# Data Cleaning with dataframe object values and return the dataframe
def clean_data(df):
    """
    Data Cleaning/Processing function
    params : df
    df : IT is a pandas dataframe Object
    return : Returns a pandas dataframe object
    """
    df['price'].fillna(df['price'].median(), inplace=True)
    df['quantity_sold'].fillna(df['quantity_sold'].median(), inplace=True)
    df['rating'] = df.groupby('category')['rating'].transform(lambda x: x.fillna(x.mean()))

    # Ensure numeric values for price quantity_sold and rating
    df['price'] = pd.to_numeric(df['price'], errors='coerce')
    df['quantity_sold'] = pd.to_numeric(df['quantity_sold'], errors='coerce')
    df['rating'] = pd.to_numeric(df['rating'], errors='coerce')
    return df

# Define API Data Validation Model for SignUp/SignIn Request Validation
class SignupSignInModel(BaseModel):
    username: constr(min_length=1, strip_whitespace=True)  # Ensures non-empty and strips whitespace
    password: constr(min_length=6, strip_whitespace=True)

#Environment Variables for now I am putting here for production this can be handled in .env file
SECRET_KEY = '567yhdsjkoiwesj0983uiew'


def validate_token(f):
    """
    Decorator Function to Validate JWT token
    params: function
    """
    @wraps(f)
    def verify(*args, **kwargs):
        token = None
        # Check if the token is present in the request headers
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            token = auth_header.split(" ")[1] if "Bearer" in auth_header else None
        if not token:
            return jsonify({'message': 'Token is missing'}), 401
        # Decode the token to check validity and expiration
        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token'}), 401
        return f(*args, **kwargs)
    return verify

# Create Flask Application Object
app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY


@app.route('/signup', methods=['POST'])
def signup():
    """
    SignUp/ User Registration API
    params: Username and Password
    """
    try:
        data = request.get_json()
        user_data = SignupSignInModel(**data)
        password_hash = bcrypt.hashpw(user_data.password.encode('utf-8'), bcrypt.gensalt())
        engine = connect_db()
        Session = sessionmaker(bind=engine)
        session = Session()
        user = User(username=user_data.username, password_hash=password_hash)
        session.add(user)
        session.commit()
        return jsonify({'message': 'User created successfully'}), 201
    except ValidationError as e:
        return jsonify({'error': e.errors()}), 400
    except Exception as e:
        return jsonify({'message': 'Something went wrong'}), 500


@app.route('/login', methods=['POST'])
def login():
    """
    Login API
    params: Username and Password
    """
    try:
        data = request.get_json()
        user_data = SignupSignInModel(**data)
        engine = connect_db()
        Session = sessionmaker(bind=engine)
        session = Session()
        user = session.query(User).filter_by(username=user_data.username).first()

        # Check User and password exists and validate password
        if user and bcrypt.checkpw(user_data.password.encode('utf-8'), user.password_hash.encode('utf-8')):

            # Generate login token
            token = jwt.encode({'username': user_data.username, 'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)},
                               SECRET_KEY)
            return jsonify({'access_token': token}), 200
        else:
            return jsonify({'message': 'Invalid credentials'}), 401
    except ValidationError as e:
        return jsonify({'errors': e.errors()}), 400
    except Exception as e:
        return jsonify({'message': 'Something went wrong'}), 500


# API endpoint to Clean data and Upload Product details to products table
@app.route('/load_csv', methods=['POST'])
@validate_token
def load_csv():
    """
    Load csv file end points will be used for the reading csv files and uploading data to the products table
    """
    try:
        request_data = request.get_json()
        if not request_data.get("file_path"):
            return jsonify({'message': 'Csv file path is mandatory'}), 200
        csv_file_path = request_data.get("file_path") # Overwrite here for custom path
        df = pd.read_csv(csv_file_path)
        cleaned_df = clean_data(df)
        engine = connect_db()
        cleaned_df.to_sql('products', con=engine, if_exists='append', index=False)
        return jsonify({'message': 'Csv data successfully loaded to mysql' }), 201
    except Exception as e:
        return jsonify({'message': 'Something went wrong'}), 500


# Summary Report access api endpoint for mandatory JWT token
@app.route('/summary', methods=['GET'])
@validate_token
def summary_report():
    """
    This api will create summary report csv file and also return the summary data to api response.
    """
    try:
        engine = connect_db()  #
        df = pd.read_sql('products', con=engine)
        summary_df = df.groupby('category').agg(
            total_revenue=pd.NamedAgg(column='price', aggfunc='sum'),
            top_product_quantity_sold=pd.NamedAgg(column='quantity_sold', aggfunc='max')
        ).reset_index()

        # Find top product form each category
        for category in summary_df['category']:
            top_product = df[df['category'] == category].sort_values(by='quantity_sold', ascending=False).iloc[0]
            summary_df.loc[summary_df['category'] == category, 'top_product'] = top_product['product_name']

        # Save Report to CSV
        summary_df.to_csv('summary_report.csv', index=False)
        return jsonify({'message': 'Summary Report successfully generated',
            'data': summary_df.to_dict(orient='records')}), 200
    except Exception as e:
        return jsonify({'message': 'Something went wrong'}), 500


if __name__ == '__main__':
    app.run(debug=True)


