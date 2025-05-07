# Social network back-end with AI moderation

## Description
App features back-end application in FastAPI with SQLite database, handled by SQLAlchemy + Pydantic.
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
cd starnavi-backend-app
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

## Testing

App provides tests for each function and feature with pytest. They are located in app/tests folder.

To launch tests, call `pytest` command in venv.

### Testing scenarios:

#### Test auth:
 - test_create_user - Verifies, that user can be created via api/register endpoint. Sends request to endpoint, checks
 status code and response body. Also verifies, that user profile was automatically created;
 - test_create_user_existing_username - Verifies, that user cannot be created, if username already exists in database.
 Sends request to api/register with the same username as in previous test, verifies response error;
 - test_login_user - Verifies, that with provided credentials for registered user, access token can be obtained.
 Sends request to api/login endpoint with username and passwords, checks response body for access_token field. Saves token
 for further usage. ;
 - test_refresh_access_token - Verifies, that access token can be refreshed via api/refresh-access-token-endpoint.
 Sends request to endpoint with previously obtained access token, checks response body for access token field;
 - test_my_profile - Verifies, that with given access token, user profile for that token can be obtained.
 Send request to api/my-profile endpoint, checks response body for "bio" field;
 - test_delete_user - Verifies, that with given access_token, user profile can be deleted. Sends delete request to
 api/user and check response body for successful deletion indication message.

#### Test comment:
 - test_create_comment - Creates two users, creates post, creates comment from each of two users. Verifies creation
 status codes, and comment content and author_id from body response;
 - test_create_harmful_comment - Verifies, that comment with harmful content cannot be created. Sends request
 for creating comment with harmful content, verifies response error code.
 - test_create_comment_unauthenticated - Verifies, that comment cannot be created without provided credentials;
 - test_list_comments - Verifies, that list of comments for specific post can be retrieved.
 - test_update_comment - Verifies, that comment can be updated by its author.
 - test_update_comment_unauthenticated - Verifies, that comment cannot be updated if no credentials were provided.
 - test_update_comment_unauthorized - Verifies, that comment can not be updated, if given access token user is not
 author of a post.
 - test_delete_comment - Deletes previously created comments.
 - test_comments_daily_breakdown - Test for comments daily breakdown feature. Creates five comments, calls
 /api/comments-daily-breakdown with query params for today's date, checks response body for those comments.
 - test_auto_reply_feature - Test for auto_reply feature. Sends request to update user profile to turn on feature for
 user, creates post, creates comment from another user. Gets list of comments for that post via endpoint, ensures,
 that response body contains comment, generated by LLM.

#### Test moderation
 - test_moderate_content_service - Test for content moderation service. Calls moderation service with two strings -
 one harmless, one harmful. Ensures, that service marked those strings accordingly.


#### Test post
 - test_create_post - This test creates two posts by two different users and ensures, that post can be created by user;
 - test_create_post_unauthenticated - Test the post creation endpoint in case, where no authentication credentials provided.
 - test_list_posts - This test ensures, that list of posts can be retrieved.
 - test_get_post - This test ensures that a post can be retrieved by its id.
 - test_update_post - This test ensures, that post can be updated by its author;
 - test_update_post_unauthenticated - Test for update post endpoint in case, where no credentials were provided;
 - test_update_post_unauthorized - Test for update post endpoint, where current user is not author of the post;
 - test_delete_post - Deletes previously created post.

#### Test user
 - test_get_user_profile - This test ensures that a user's profile can be retrieved by their ID.

## Directories structure

 - /alembic.ini - Config for alembic - tool, that handles database migrations
 - /generate_jwt_secret.py - Script, that generates JWT secret and saves it to .env
 - /requirements.txt - Project dependencies
 - /README.md - This file
 - /alembic/ - Folder with Alembic tool for database migrations
 - /database/ - Folder with database.db file
 - /app - Application folder
 - /app/main.py - Main function of an app. Initiates FastAPI and routers
 - /app/database.py - Configuration of database connection
 - /core/ - Application config directory
 - /core/config.py - Sets up settings, particularly OpenAI API key
 - /core/security.py - Config for JWT authorization
 - /models/ - Directory with corresponding ORM models
 - /routers/ - Directory with corresponding FastAPI routers
 - /schemas/ - Directory with corresponding Pydantic schemas
 - /services/ - Directory with additional features services
 - /services/auto_reply_to_comment.py - Handles auto reply to comments feature
 - /services/llm_moderation.py - Handles OpenAI moderation feature
 - /tests/ - Directory with tests

## API Reference

### Authentication

<details>
  <summary>POST /api/register</summary>

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
</details>

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
 - Make user creation enpoint returnd 201 CREATED status code instead of 200 OK
