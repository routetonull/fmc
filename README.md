# fmc.py

License: [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/)

*USE AT YOUR OWN RISK*

## Example of use

*Note: create a different user on FMC for API use, one session per user at a time is permitted*

Connect to FMC

	import fmc
	f = fmc.Fmc("10.0.0.254","myusername","myverysecretpassword")
	f.connect()

Get help 

	help(f)

**Host create and delete**

Search non existent host

	f.findHost("test")
	[]

Add host

	f.addHost("test","10.99.99.99","this is a test")

Search again and see host details

	f.findHost("test")
	[{'id': '005AAAAA-AAAA-AAAA-0000-AAAAAAAAAAAA', 'links': {'parent': 'https://10.0.0.254/api/fmc_config/v1/domain/AAAAAAAA-BBBB-CCCC-DDDD-EEEEEEEEEEEE/object/networkaddresses', 'self': 'https://10.0.0.254/api/fmc_config/v1/domain/AAAAAAAA-BBBB-CCCC-DDDD-EEEEEEEEEEEE/object/hosts/AAAAAAAA-BBBB-CCCC-DDDD-EEEEEEEEEEEE'}, 'name': 'test', 'type': 'Host'}]

Get host ID

	id = f.findHost("test")[0]['id']

Delete host providing its ID

	f.delHost(id)

Search again, host is gone

	f.findHost("test")
	[]

Show all host objects

	f.showHosts()

Show all network objects

	f.showNetworks()


Enjoy!