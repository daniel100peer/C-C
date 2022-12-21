# C-C
a command controller 

•	Server side - Manage all connected agents, by using keep alive messages, and has the ability to dispatch commands for execution to available agents and receive output results.
•	Client side – Agent that connects to a command controller and waits for incoming command for execution.

•	Client:
1.	The client has a predefined configuration file which will be referenced as “(configuration)” through out the document.
2.	Write a client agent that on startup connects to its server by IP:PORT (configuration), and sends keep alive messages to the server at a configurable interval.
3.	The client should listen for incoming command messages from its C&C, while the command message structure should be as follows: 
-	command payload (of type: byte array)
-	command type (of type int/string), 
-	command identifier (unique ID, each command must have a unique identifier) (of type: int), 
-	command payload arguments (of type: string array).
4.	When a new message is received from the server. The command payload should be saved as a file (so / python / etc… dependent on the language of your choosing) in a designated directory (configuration).
5.	The client loads the payload file (mentioned in step 4) and runs a specific method (known in advance) according to a known function signature, with the received arguments from the “command payload arguments”.
An example for command payload file could be: 
-	file upload command
-	shell execution command
-	port scanning command
-	etc.
6.	The client should transmit to the server the status of the command execution process, i.e. Received, Initialized, Running, Finished or Error.
7.	The client will transmit the command execution results in base64 encoding to the server if it was a successfully executed, or an error message if failed, with the “command identifier”.
8.	The client should manage incoming command in a queue and then execute each command in a different thread/process.
9.	The client will delete the command execution file after the result have been sent to the C&C.

