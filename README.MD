# VOIP Connection

There are no required packages, the transfer protocol used only built in python packages

1. running the main.py with 'python3 src/main.py' will run a VOIP connection through the network sim, make sure you have a mic connected to test it.

### Since this is running through a network sim, it outputs audio on the same device as the input which results in an echo. Highly recommended to mute Audio when testing because of this.

2. Press ctr+c to end the connection, this will also save the audio sent as 'sent_live_audio'.wav and received audio as 'received_live_audio'.wav. These two files should be nearly identically to prove the VOIP connectio was working properly.

3. Arguments that can be added:
    
    1.  --ip: Manually choose ip for the VOIP connection
            ex: 'python3 src/main.py --ip='127.0.0.8'
    
    3.  --receiver-port, -sp: Manually choose port for the receiver to use
            ex: 'python3 src/main.py --receiver_port=12345'

    4.  --proxy-port, -pp: Manually choose port for the proxy to use
            ex: 'python3 src/main.py --proxy_port=12345'