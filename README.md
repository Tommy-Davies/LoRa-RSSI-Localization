<h1>locServer</h1>
<p>
Functions as both a localization node and as a server to calculate and display the location of the localized node.
</p>
<p>
Receives two types of packets: pings to calculate RSSI when used as a node, and data packets that aggregate the RSSI from all three nodes and sensor information. Sends a simple acknowledge to pings, and parses and processes data packets.
</p>

<h1>localizedNode</h1>
<p>
Sends multiple pings to all nodes and stores their RSSI values. Formats information into a delimited string and sends to raspberry pi server as a data packet.
</p>

<h1>receiveNode</h1>
<p>
Receive pings from localized node and send an acknowledge to calculate RSSI.
</p>

<h1>mqttPublisher</h1>
<p>
Sends calculated cartesian coordinates and sensor data over mqtt on the rssi topic. Intended to be received by mqttReceiver and displayed on a GUI, but could be used by anything as its just a formatted string.
</p>

<h1>mqttReceiver</h1>
<p>
Subscribes to rssi mqtt topic and waits for messages to come from raspberry pi server. Parses data string and displays on GUI.
</p>
