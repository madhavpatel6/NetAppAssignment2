Libraries Required:
    sudo apt-get install
	blueman
	bluez
	bluetooth
	rabbitmq-server
	mongodb-server

    pip3 install
	pybluez
	pika
	pymongo
	pickle
	json

Bluetooth Pairing:
	1. On both raspberry pi's open up a command console and run 'sudo bluetoothctl'
	2. On one pi's console run these commands 'agent on' + 'default-agent on' + 'discoverable on'
	3. Once you type discoverable on the one pi use the other pi to pair with that pi
		by clicking on the bluetooth icon in the top right corner and then select
		add device. You may need to wait a second before your raspberry pi appears
		as an option but once that comes up click on the link.
	4. A couple prompts will pop up on both devices to confirm passwords and confirm 
		if you want to pair. Click yes or confirm on all the prompts.
	5. On both devices in the console you should now see pair successful and you can
		now use a bluetooth socket to communicate between the two devices. In order
		to run the scripts the send addresses will need to be update with your raspberry
		pi's addresses such that the messages will be sent to the correct devices.

Zeroconf:
	1. On the repository create the following file at /etc/avahi/services/multiple.service
	The contents of the file:
<?xml version="1.0" standalone='no'?>
<!DOCTYPE service-group SYSTEM "avahi-service.dtd">
<service-group>
        <name replace-wildcards="yes">%h</name>
        <service>
                <type>_device-info._tcp</type>
                <port>0</port>
                <txt-record>model=RackMac</txt-record>
        </service>
        <service>
                <type>_ssh._tcp</type>
                <port>22</port>
        </service>
</service-group>
	2. Change the host name of the raspberrypi to avoid IP conflicts. To do this edit /etc/hosts
		and replace raspberrypi with your preferred host name. Additionally, edit /etc/hostname
		and replace raspberrypi with your preferred host name.
	3. Reboot the raspberrypi

	
	