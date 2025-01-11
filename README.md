# PocketSense API Documentation

PocketSense is a platform designed to help college students track and split daily expenses with friends. This documentation covers the API endpoints for user registration, login, group management, expense tracking, and retrieving user-specific expenses.

---

## Base URL

```
http://127.0.0.1:8000/api/
```

---

## Endpoints

### 1. User Registration

**URL:** `/register/`  
**Method:** `POST`

**Request Body:**

```json
{
  "username": "john1",
  "first_name": "John",
  "last_name": "Doe",
  "email": "johndoe1@gmail.com",
  "password": "12345678",
  "password1": "12345678"
}
```

**Response:**

```json
{
  "message": "User registered successfully",
  "success": true
}
```

---

### 2. User Login

**URL:** `/login/`  
**Method:** `POST`

**Request Body:**

```json
{
  "email": "johndoe@gmail.com",
  "password": "12345678"
}
```

**Response:**

```json
{
  "message": "User login successfully",
  "success": true,
  "access": "<JWT_ACCESS_TOKEN>"
}
```

> Save the `access` token from the response for authenticated requests.

---

### 3. Group Management

**URL:** `/groups/`  
**Method:** `GET`, `POST`

#### Create a Group

**Request Body:**

```json
{
  "name": "Tour To Sylhet",
  "description": "Group for go to Sylhet",
  "members": ["mohosin", "john"]
}
```

**Response:**

```json
{
  "message": "Group created successfully",
  "group": {
    "id": 1,
    "name": "Tour To Sylhet",
    "description": "Group for go to Sylhet",
    "members": ["mohosin", "john"]
  }
}
```

#### List Groups

**Response:**

```json
[
  {
    "id": 1,
    "name": "Tour To Sylhet",
    "description": "Group for go to Sylhet",
    "members": ["mohosin", "john"]
  }
]
```

---

### 4. Expense Management

**URL:** `/expenses/`  
**Method:** `GET`, `POST`

#### Add an Expense

**Request Body:**

```json
{
  "group": "Tour To Sylhet",
  "description": "Breakfast",
  "amount": 1000,
  "paid_by": "mohosin",
  "split_among": ["mohosin", "john"]
}
```

**Response:**

```json
{
  "message": "Expense added successfully",
  "expense": {
    "id": 1,
    "group": "Tour To Sylhet",
    "description": "Breakfast",
    "amount": 1000,
    "paid_by": "mohosin",
    "split_among": ["mohosin", "john"]
  }
}
```

#### List Expenses

**Response:**

```json
[
  {
    "id": 1,
    "group": "Tour To Sylhet",
    "description": "Breakfast",
    "amount": 1000,
    "paid_by": "mohosin",
    "split_among": ["mohosin", "john"]
  }
]
```

---

### 5. User-Specific Expenses

**URL:** `/user-expenses/`  
**Method:** `GET`

#### Header:

- **Authorization:** Bearer `<JWT_ACCESS_TOKEN>`

**Response:**

```json
{
  "user": "john",
  "expenses": [
    {
      "group": "Tour To Sylhet",
      "description": "Breakfast",
      "amount": 500,
      "paid_by": "mohosin",
      "share": 500
    }
  ]
}
```

---

## Notes

- Replace `<JWT_ACCESS_TOKEN>` with the access token from the login response.
- Use a tool like Postman to test the APIs.
- Ensure proper error handling for invalid requests or expired tokens.

---

## Contributing

Feel free to contribute by submitting issues or pull requests to improve the API.

---

## License

This project is licensed under the MIT License.
