# Social network back-end with AI moderation

## Description
App features back-end application in FastAPI with SQLite database.
Supports users, posts and comments with corresponding endpoints and JWT authentication

Additional features:
    - Moderation of content using OpenAI moderation llm - posts and comments content are getting
    checked for potentially harmful content before creation, and if moderation service will mark them as ones, they
    will not be created, returning corresponding error.
    - Auto-reply using LLM (OpenAI API) after previously set amount of time.
    - Comment statistics endpoint, that returns comments and their amount for specified range of days.

## Installation

### Prequisites
    Python (3.11 or higher)
    Git

### Clone the repo
Clone repo to your local machine:
```
git clone https://github.com/rzlodeev/starnavi-backend-app.git
cd starnavi-backend-app.git
```

### Setup virtual environment
Create and activate virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

### Install the necessary packages using pip:

```bash
pip install -r requirements.txt
```

### Create .env file in project root directory (where requirements.txt located) and add OpenAI API key
```
OPENAI_API_KEY=xxxxxxxxxx
```

### Generate JWT secret key using script generate_jwt_secret.py
```
python3 generate_jwt_secret.py
```

Now you can launch the app!

## Usage

### Launch server
```
uvicorn app.main:app --reload
```

Server should launch locally on ```http://127.0.0.1:8000```

Now you can send requests. You can find detail API documentation at the end of the file.

### Usage example via bash curl (or any other service like Postman):

 - Register 2 users. Second user will be used for testing auto-reply feature - it can be triggered only if
 comment author is _not_ author of the post.

```bash
curl -X POST http://127.0.0.1:8000/api/register \
     -H "Content-Type: application/json" \
     -d '{
           "username": "dyadya vasya",
           "email": "qwerty@uiop.com",
           "password": "sheesh"
         }'
```


```bash
curl -X POST http://127.0.0.1:8000/api/register \
     -H "Content-Type: application/json" \
     -d '{
           "username": "dyadya misha",
           "email": "asdfgh@jkl.com",
           "password": "sheesh"
         }'
```

- Login to obtain access_token

```bash
curl -X POST http://127.0.0.1:8000/api/login \
     -F "username=dyadya vasya" \
     -F "password=sheesh"
```

should return

```
{
    "access_token": "ACCESS_TOKEN",
    "token_type": "bearer"
}
```

with actual access token instead of ACCESS_TOKEN. Copy that access token, you will use it later.
Also obtain access_token for second user.

 - Enable auto-reply feature and set delay to 2 minutes

```bash
curl -X PATCH http://127.0.0.1:8000/api/user \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer ACCESS_TOKEN"
     -d '{
           "auto_respond_to_comments": true,
           "auto_respond_time": 2
         }'
```

 - Create post

```bash
curl -X POST http://127.0.0.1:8000/api/posts \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer ACCESS_TOKEN"
     -d '{
           "title": "I am dyadya vasya",
           "content": "Do you folks want to know how to install kali linux in windows using wsl and have some fun with it?"
         }'
```

- Create comment from second user
```bash
curl -X POST http://127.0.0.1:8000/api/posts/1/comments \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer ACCESS_TOKEN_FOR_SECOND_USER"
     -d '{
           "content": "Of course we do, please tell us how!"
         }'
```

 - Wait for 2 minutes, and check comments

```bash
curl -X GET http://127.0.0.1:8000/api/posts/1/comments
```


should return you something like

```
[
    {
        "id": 1,
        "content": "Of course we do, please tell us how",
        "created_at": "1337-04-20T04:19:00.000000",
        "owner_id": 1,
        "post_id": 1
    },
    {
        "id": 2,
        "content": "Sure thing! First, you need to enable WSL in Windows features, then install Kali Linux from the Microsoft Store. Once installed, set up your username and password. You can then start having fun exploring all the tools Kali Linux offers right on your Windows system. Enjoy! \\n",
        "created_at": "1337-04-20T04:20:00.000000",
        "owner_id": 2,
        "post_id": 1
    }
]
```

with second comment auto created by LLM.

If you will try to create harmful comment, system will not let you do it. Give it a try:
```bash
curl -X POST http://127.0.0.1:8000/api/posts/1/comments \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer ACCESS_TOKEN"
     -d '{
           "content": "VERY_INAPPROPRIATE_COMMENT"
         }'
```

Replace VERY_INAPPROPRIATE_COMMENT with most inappropriate content known to mankind. Use your fantasy and let yourself
have some fun - you deserve it. Blocked comments will also have flags with blocking reasoning, one or several of hate,
hate/threatening, harassment, harassment/threatening, self-harm, self-harm/intent, self-harm/instructions, sexual,
sexual/minors, violence, violence/graphic. Collect 'em all!

 - Get comment statistics for today:

```bash
curl -X GET "http://127.0.0.1:8000/api/comments-daily-breakdown?date_from=1337-04-20&date_to=1337-04-20"
```

Replace `date_from` and `date_to` with today\'s date.

It should return you:

```
{
    "comments": {
        "1337-04-20": {
            "items": [
                {
                    "id": 1,
                    "content": "Of course we do, please tell us how",
                    "created_at": "1337-04-20T04:19:00.000000",
                    "owner_id": 1,
                    "post_id": 1
                },
                {
                    "id": 2,
                    "content": "Sure thing! First, you need to enable WSL in Windows features, then install Kali Linux from the Microsoft Store. Once installed, set up your username and password. You can then start having fun exploring all the tools Kali Linux offers right on your Windows system. Enjoy! \\n",
                    "created_at": "1337-04-20T04:20:00.000000",
                    "owner_id": 2,
                    "post_id": 1
                }
            ],
            "comments_amount": 2
        }
    },
    "blocked_comments": {
        "1337-04-20":
            "items": [
                {
                    "id": 1,
                    "content": "very inappropriate comment",
                    "created_at": "1337-04-20T04:20:00.000000",
                    "owner_id": 1,
                    "post_id": 1
                    "blocking_reasoning": "violence, harassment"
                }
            ]
        }
    },
    "total_comments_amount": 2,
    "total_blocked_comments_amount": 1
}
```

## API Reference

### Authentication

<details>
    <summary>POST `/api/register`</summary>

    Register a new user.

    Request body example:

    ```
    {
      "username": "string",
      "email": "user@example.com",
      "password": "string"
    }
    ```

    Responses:

     - Code *200*

     Registered user object

     ```
     {
         "id": 0,
        "username": "string",
        "email": "user@example.com",
        "auto_respond_to_comments": true,
        "auto_respond_time": 0
     }
    ```

     - Code *422*

     Validation error. Triggers if request is not properly formatted.

     ```
     {
        "detail": [
            {
                "type": "missing",
                "loc": [
                    "body",
                    "username"
                ],
                "msg": "Field required",
                "input": null
            },
            {
                "type": "missing",
                "loc": [
                    "body",
                    "password"
                ],
                "msg": "Field required",
                "input": null
            }
        ]
     }
    ```

    - Code *500*

    Triggers with database error.

    ```
    {
        "detail": ""An database error occurred while deleting the user profile: ERROR_MESSAGE""
    }
    ```
</details>

<details>
    <summary>POST `/api/login`</summary>
    Login to obtain access token.

    Request form-data parameters:

    `username` - string *required*
    `password` - string *required*

    Responses:

     - Code *200*

     Access token and type

     ```
     {
        "access_token": "ACCESS_TOKEN",
        "type": "bearer"
     }
    ```

     - Code *422*

     Validation error. Triggers if request is not properly formatted.

     ```
     {
        "detail": [
            {
                "type": "missing",
                "loc": [
                    "body",
                    "username"
                ],
                "msg": "Field required",
                "input": null
            },
            {
                "type": "missing",
                "loc": [
                    "body",
                    "password"
                ],
                "msg": "Field required",
                "input": null
            }
        ]
     }
    ```

    - Code *500*

    Triggers with database error.

    ```
    {
        "detail": ""An database error occurred while deleting the user profile: ERROR_MESSAGE""
    }
    ```
</details>

<details>
    <summary>DELETE `/api/user`</summary>
    Delete current user profile

    Request headers:

    ```
    Authentication: Bearer ACCESS_TOKEN
    ```

    Responses:

     - Code *200*

     Message indicating the deletion status

     ```
     {
        "message": "User %username% was deleted successfully"
     }
    ```

    - Code *401* UNAUTHENTICATED

    Triggers when credentials were not provided or they are invalid.

    ```
    {
        "detail": "Could not validate credentials"
    }
    ```

    - Code *500*

    Triggers with database error.

    ```
    {
        "detail": ""An database error occurred while deleting the user profile: ERROR_MESSAGE""
    }
    ```
</details>

<details>
    <summary>PATCH `/api/user`</summary>
    Update profile endpoint.

    Request headers:

    ```
    Authentication: Bearer ACCESS_TOKEN
    ```

    Request body example:

    ```
    {
        "username": "string",
        "email": "string",
        "auto_respond_to_comments": true,
        "auto_respond_time": 0
    }
    ```

    None of fields are required, but request should contain at least one of them.

    Responses:

     - Code *200*

     Updated user object

    ```
    {
        "username": "string",
        "email": "string",
        "auto_respond_to_comments": true,
        "auto_respond_time": 0
    }
    ```

     - Code *422*

     Validation error. Triggers if request is not properly formatted.

     ```
     {
        "detail": [
        {
            "type": "missing",
            "loc": [
                "body"
            ],
            "msg": "Field required",
            "input": null
        }]
    }
    ```

    - Code *401*

    Triggers when credentials were not provided or they are invalid.

    ```
    {
        "detail": "Could not validate credentials"
    }
    ```

    - Code *500*

    Triggers with database error.

    ```
    {
        "detail": ""An database error occurred while deleting the user profile: ERROR_MESSAGE""
    }
    ```
</details>

<details>
    <summary>GET `/api/my-profile`</summary>
    Get authenticated user profile.

    Request headers:

    ```
    Authentication: Bearer ACCESS_TOKEN
    ```

    Responses:

     - Code *200*

     User profile object

    ```
    {
        "id": 0,
        "user_id": 0,
        "bio": "string",
        "profile_picture": "string"
    }
    ```

    - Code *401*

    Triggers when credentials were not provided or they are invalid.

    ```
    {
        "detail": "Could not validate credentials"
    }
    ```

    - Code *500*

    Triggers with database error.

    ```
    {
        "detail": ""An database error occurred while deleting the user profile: ERROR_MESSAGE""
    }
    ```
</details>

<details>
    <summary>GET `/api/refresh-access-token`</summary>
    Exchange existing access token for a new one.

    Request headers:

    ```
    Authentication: Bearer ACCESS_TOKEN
    ```

    Responses:

     - Code *200*

     Access token and type

     ```
     {
        "access_token": "ACCESS_TOKEN",
        "type": "bearer"
     }
    ```

    - Code *401*

    Triggers when credentials were not provided or they are invalid.

    ```
    {
        "detail": "Could not validate credentials"
    }
    ```

    - Code *500*

    Triggers with database error.

    ```
    {
        "detail": ""An database error occurred while trying to refreshing token: ERROR_MESSAGE""
    }
    ```
</details>

### Posts

<details>
    <summary>GET `/api/posts`</summary>
    List all posts.

    Responses:

     - Code *200*

     List of post objects

     ```
     [
        {
        "id": 0,
        "title": "string",
        "content": "string",
        "owner_id": 0
        }
    ]
    ```

    - Code *500*

    Triggers with database error.

    ```
    {
        "detail": ""An database error occurred while getting posts list: ERROR_MESSAGE""
    }
    ```
</details>

<details>
    <summary>GET `/api/posts/{post_id}`</summary>
    Get specific post endpoint.

    Path parameters:
    post_id: ID of post to obtain.

    Responses:

     - Code *200*

     Post object

    ```
     {
        "id": 0,
        "title": "string",
        "content": "string",
        "owner_id": 0
    }
    ```

    - Code *404*

    Triggers, when provided post_id doesn't exist.

    ```
    {
        "detail": Post not found""
    }
    ```

    - Code *500*

    Triggers with database error.

    ```
    {
        "detail": ""An database error occurred while trying to create post: ERROR_MESSAGE""
    }
    ```
</details>

<details>
    <summary>PUT `/api/posts/{post_id}`</summary>
    Update post.

    Path parameters:
    post_id: ID of post to update.

    Request headers:

    ```
    Authentication: Bearer ACCESS_TOKEN
    ```

    Request body:

    ```
    {
        "title": "string",
        "content": "string"
    }
    ```

    Responses:

     - Code *200*

     Updated post object

    ```
     {
        "id": 0,
        "title": "string",
        "content": "string",
        "owner_id": 0
    }
    ```

        - Code *401* UNAUTHENTICATED

    Triggers when credentials were not provided or they are invalid.

    ```
    {
        "detail": "Could not validate credentials"
    }
    ```

    - Code *403* UNAUTHORIZED

    Triggers when current user doesn't have permissions to perform action.

    ```
    {
        "detail": "Post can be updated only by its author."
    }
    ```

    - Code *404*

    Triggers, when provided post_id doesn't exist.

    ```
    {
        "detail": Post not found""
    }
    ```

    - Code *500*

    Triggers with database error.

    ```
    {
        "detail": ""An database error occurred while updating post: ERROR_MESSAGE""
    }
    ```
</details>

<details>
    <summary>DELETE `/api/posts/{post_id}`</summary>
    Delete post endpoint.

    Path parameters:
    post_id: ID of post to delete.

    Request headers:

    ```
    Authentication: Bearer ACCESS_TOKEN
    ```

    Responses:

     - Code *200*

     Message indicating successful deletion.

     ```
     {
        "message": "Post {post_id} was deleted successfully."
     }
    ```

    - Code *401* UNAUTHENTICATED

    Triggers when credentials were not provided or they are invalid.

    ```
    {
        "detail": "Could not validate credentials"
    }
    ```

    - Code *403* UNAUTHORIZED

    Triggers when current user doesn't have permissions to perform action.

    ```
    {
        "detail": "Post can be updated only by its author."
    }
    ```

    - Code *404*

    Triggers, when provided post_id doesn't exist.

    ```
    {
        "detail": "Post not found"
    }
    ```

    - Code *500*

    Triggers with database error.

   ```
    {
        "detail": "An database error occurred while deleting post: ERROR_MESSAGE"
    }
    ```
</details>

### Users
<details>
    <summary>GET `/api/profile/{user_id}`</summary>
    Get specific user profile.

    Path parameters:
    user_id: ID of user to obtain.

    Responses:

     - Code *200*

     Post object

     ```
     {
         "id": 0,
        "username": "string",
        "email": "user@example.com",
        "auto_respond_to_comments": true,
        "auto_respond_time": 0
     }
     ```

    - Code *404*

    Triggers, when provided user_id doesn't exist.

    ```
    {
        "detail": User not found""
    }
    ```

    - Code *500*

    Triggers with database error.

    ```
    {
        "detail": ""An database error occurred while deleting the user profile: ERROR_MESSAGE""
    }
    ```
</details>

### Comments
<details>
    <summary>GET `/api/posts/{post_id}/comments`</summary>
    List all comments for specific post.

    Path parameters:
    post_id: ID of post.

    Responses:

     - Code *200*

     List of comment objects

     ```
     [
        {
            "id": 0,
             "content": "string",
             "created_at": "2024-07-20T17:46:52.825Z",
             "owner_id": 0,
            "post_id": 0
        }
     ]
     ```

    - Code *500*

    Triggers with database error.

    ```
    {
        "detail": ""An database error occurred while trying list comments for {post_id}: ERROR_MESSAGE""
    }
    ```
</details>

<details>
    <summary>POST `/api/posts/{post_id}/comments`</summary>
    Comment creation for specific post endpoint.

    Path parameters:
    post_id: ID of post.

    Request headers:

    ```
    Authentication: Bearer ACCESS_TOKEN
    ```

    Request body:

    ```
    {
        "content": "string"
    }
    ```

    Responses:

     - Code *200*

     Created comment

     ```
     {
        "id": 0,
        "content": "string",
        "created_at": "2024-07-20T17:46:52.825Z",
        "owner_id": 0,
        "post_id": 0
     }
     ```

    - Code *401*

    Triggers when credentials were not provided or they are invalid.

    ```
    {
        "detail": "Could not validate credentials"
    }
    ```

    - Code *500*

    Triggers with database error.

    ```
    {
        "detail": ""An database error occurred while trying pto create comment for {post_id}: ERROR_MESSAGE""
    }
    ```
</details>

<details>
    <summary>#### PUT `/api/posts/{post_id}/comments/{comment_id}`</summary>
    Update comment for specific post.

    Path parameters:
    post_id: ID of post.
    comment_id: ID of comment to update.

    Request headers:

    ```
    Authentication: Bearer ACCESS_TOKEN
    ```

    Request body:

    ```
    {
        "content": "string"
    }
    ```

    Responses:

     - Code *200*

     Updated comment object

     ```
     {
        "id": 0,
        "content": "string",
        "created_at": "2024-07-20T17:46:52.825Z",
        "owner_id": 0,
        "post_id": 0
     }
     ```

    - Code *401* UNAUTHENTICATED

    Triggers when credentials were not provided or they are invalid.

    ```
    {
        "detail": "Could not validate credentials"
    }
    ```

    - Code *403* UNAUTHORIZED

    Triggers when current user doesn't have permissions to perform action.

    ```
    {
        "detail": "Comment can be updated only by its author."
    }
    ```

    - Code *404*

    Triggers, when provided post_id or comment_id doesn't exist.

    ```
    {
        "detail": "Post not found"
    }
    ```

    - Code *500*

    Triggers with database error.

    ```
    {
        "detail": ""An database error occurred while updating comment: ERROR_MESSAGE""
    }
    ```
</details>

<details>
    <summary>#### DELETE `/api/posts/{post_id}/comments/{comment_id}`</summary>
    Delete comment endpoint.

    Path parameters:
    post_id: ID of post.
    comment_id: ID of comment to delete.

    Request headers:

    ```
    Authentication: Bearer ACCESS_TOKEN
    ```

    Responses:

     - Code *200*

     Message indicating successful deletion.

     ```
     {
        "message": "Comment {comment_id} was deleted successfully."
     }
     ```

    - Code *404*

    Triggers, when provided post_id or comment_id doesn't exist.

    ```
    {
        "detail": Post not found""
    }
    ```

    - Code *401* UNAUTHENTICATED

    Triggers when credentials were not provided or they are invalid.

    ```
    {
        "detail": "Could not validate credentials"
    }
    ```

    - Code *403* UNAUTHORIZED

    Triggers when current user doesn't have permissions to perform action.

    ```
    {
        "detail": "Comment can be deleted only by its author."
    }
    ```

    - Code *500*

    Triggers with database error.

    ```
    {
        "detail": ""An database error occurred while deleting post: ERROR_MESSAGE""
    }
    ```
</details>

<details>
    <summary>#### GET `/api/comments-daily-breakdown`</summary>
    Get comments for specified range of time.

    Query parameters:
    date_from: Start date (included) *required
    date_to: End date (included) *required

    Request example:
    ```
    /api/comments-daily-breakdown/?date_from=1337-04-19&date_to=1337-04-20
    ```

    Responses:

    - Code *200*

    Statistics for comments

    ```
    {
    "comments": {
        "2024-07-20": {
            "items": [
                {
                    "id": 39,
                    "content": "Of course we do!",
                    "created_at": "2024-07-20T19:32:44.070997",
                    "owner_id": 1,
                    "post_id": 4
                },
                {
                    "id": 40,
                    "content": "Sure thing! Installing Kali Linux in Windows using WSL is a great way to have fun and learn at the same time. Don't hesitate to give it a try! 🐧💻\\n",
                    "created_at": "2024-07-20T19:33:45.475547",
                    "owner_id": 3,
                    "post_id": 4
                },
                {
                    "id": 41,
                    "content": "Of course we do, please tell us how",
                    "created_at": "2024-07-20T19:35:42.604288",
                    "owner_id": 1,
                    "post_id": 4
                },
                {
                    "id": 42,
                    "content": "Sure thing! First, you need to enable WSL in Windows features, then install Kali Linux from the Microsoft Store. Once installed, set up your username and password. You can then start having fun exploring all the tools Kali Linux offers right on your Windows system. Enjoy! \\n",
                    "created_at": "2024-07-20T19:36:44.043891",
                    "owner_id": 3,
                    "post_id": 4
                }],
                "comments_amount": 4
            }
        },
        "blocked_comments": {},
        "total_comments_amount": 4,
        "total_blocked_comments_amount": 0
    }
    ```


## Database schemas

#### blocked_comments

 - "id" INTEGER NOT NULL
 - "content" TEXT
 - "created_at" DATETIME NOT NULL
 - "owner_id" INTEGER
 - "post_id" INTEGER
 - "blocking_reasoning" TEXT

#### comments

 - "id" INTEGER NOT NULL
 - "content" TEXT
 - "created_at" DATETIME NOT NULL
 - "owner_id" INTEGER
 - "post_id" INTEGER

#### posts
 - "id" INTEGER NOT NULL
 - "title" VARCHAR
 - "content" TEXT
 - "owner_id" INTEGER

#### user_profiles
 - "id" INTEGER NOT NULL
 - "user_id" INTEGER
 - "bio" VARCHAR
 - "profile_picture" VARCHAR

#### users
 - "id" INTEGER NOT NULL
 - "username" VARCHAR
 - "email" VARCHAR
 - "hashed_password" VARCHAR
 - "auto_respond_to_comments" BOOLEAN
 - "auto_respond_time" INTEGER

## TODO
 - Add CORS
 - Add long-live token
