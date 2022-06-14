# **watten-py**

A Python Project to Play "Watten" online.

>~~TO everyone who doesn't know Watten LEAVE!!~~
> 
>~~(Nah just don't use this project because you don't need to)~~

## What is this project based on

It is currently based on 
 - [Kivy](https://kivy.org)
 - [Twisted](https://twistedmatrix.com/)

## How can I use the program?

1. Download the [source code](https://github.com/GozZzer/watten-py-tw/archive/refs/heads/master.zip)
2. Unzip the file
3. Start the [server.py](https://github.com/GozZzer/watten-py-tw/blob/master/server.py) File
4. Open the [client.py](https://github.com/GozZzer/watten-py-tw/blob/master/client.py) File 
<br>Change the IP-Address to the IP-Address of the server
    ```python
    from watten_py import WattenClient
    
    client = WattenClient()
    client.run(host="YOUR-HOST-ADDRESS", port=5643)
    ```
5. Start as many [client.py](https://github.com/GozZzer/watten-py-tw/blob/master/client.py) Files as you want
