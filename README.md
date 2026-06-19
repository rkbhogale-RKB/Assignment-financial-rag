# Assignment-financial-rag
Assignment by Rohit Bhogale

This is an set of Financial Document APIs where we can register user, then login and get jwt token so to authorize yourself to upload document and then index it into vector DB and then finally find the reranked chunks which are revelant to query. The project will give top 20 similar or revelant chunks of the query based on documents and then apply reranking to give top 5 similar chunks based on scores.
![alt text](image.png)

1. first we create user here , with username , email and password.
<img width="1501" height="644" alt="image" src="https://github.com/user-attachments/assets/90e8201a-3f4d-4b53-bd89-1af589354f8e" />

2. Then it will store this data of user in PostgreSQL(neon cloud provider)
<img width="1393" height="482" alt="image" src="https://github.com/user-attachments/assets/adc7d908-5210-4265-aacb-b6c921f3da5d" />

3. Login with the username and password, we get an JWT token
<img width="988" height="666" alt="image" src="https://github.com/user-attachments/assets/042b72f0-6085-4314-ace6-1a85ee6ad8c9" />

4. You can upload document only after login and you need respective permissions for that suppose you are admin you get all permission , if yu are client you get view permission.
<img width="1492" height="882" alt="image" src="https://github.com/user-attachments/assets/8b53b60d-8b56-4fe9-becc-d4e9ca668f3e" />


5. After uploading we have to index it with vectorDB
<img width="1520" height="715" alt="image" src="https://github.com/user-attachments/assets/b0fc2165-61f8-40b8-8079-96e532957348" />

6. After we can give an query to the rag/search , which returns the top 5 chunks based on reranking scores.
we have used an sample 
![alt text](image-1.png)



