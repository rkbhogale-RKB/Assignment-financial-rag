# Assignment-financial-rag
Assignment by Rohit Bhogale

This is an set of Financial Document APIs where we can register user, then login and get jwt token so to authorize yourself to upload document and then index it into vector DB and then finally find the chunks which are revelant to query. The project will give top 20 similar or revelant chunks of the query based on documents.
<img width="1919" height="696" alt="image" src="https://github.com/user-attachments/assets/b1ee4084-d41d-476a-b535-97c6cd6f8729" />

1. first we create user here , with username , email and password.
<img width="1501" height="644" alt="image" src="https://github.com/user-attachments/assets/90e8201a-3f4d-4b53-bd89-1af589354f8e" />

2. Then it will store this data of user in PostgreSQL(neon cloud provider)
<img width="1393" height="482" alt="image" src="https://github.com/user-attachments/assets/adc7d908-5210-4265-aacb-b6c921f3da5d" />

3. Login with the username and password, we get an JWT token
<img width="988" height="666" alt="image" src="https://github.com/user-attachments/assets/042b72f0-6085-4314-ace6-1a85ee6ad8c9" />

4. You can upload document only after login. 
<img width="1492" height="882" alt="image" src="https://github.com/user-attachments/assets/8b53b60d-8b56-4fe9-becc-d4e9ca668f3e" />


5. After uploading we have to index it with vectorDB
<img width="1520" height="715" alt="image" src="https://github.com/user-attachments/assets/b0fc2165-61f8-40b8-8079-96e532957348" />

6. After we can give an query to the rag/search , which returns the top 20 similar chunks
<img width="1388" height="628" alt="image" src="https://github.com/user-attachments/assets/ec039704-fcca-4c79-8bdc-94b96f3d8757" />

