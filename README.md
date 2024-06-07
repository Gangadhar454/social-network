## Requirements
1. Latest version of `docker` and `docker compose` [Link](https://docs.docker.com/engine/install/ubuntu/)
2. After installing `docker` and `docker compose` , do post installation steps [Link](https://docs.docker.com/engine/install/ubuntu/)

## Getting started
1. After cloning the Repo, go to the main directory where `compose.yml` exists
2. Build the docker container
   ```
   docker compose build
   ```
    if post installation steps are not done use
   ```
   sudo docker compose build
   ```
3. Start the docker container
   ```
   docker compose up
   ```
    if post installation steps are not done use
   ```
   sudo docker compose up
   ```
The django application will start running on port `8000`

The API collection [Postman link](https://www.postman.com/research-operator-22062744/workspace/my-workspace/collection/36031344-abd06725-a7a8-43ce-87e9-f4fe8c8bca8d?action=share&creator=36031344)
