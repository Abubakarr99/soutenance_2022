# wireguard


# Description

This role setup wireguard between two endpoints. Wireguard is a type of VPN tunnel. It is fast and easy to setup. 

# Host Definition

If you want to set up a tunnel between two endpoints the endpoints should be defined at __group_vars/wireguard-interco.yaml__

You would first have to define the parameters of the endpoints and then peer the two together. 
The peer definitions should {{ inventory_hostname }}_peer. Unless this in not the desired way, in that the wireguard role. 
The variable is called __wireguard_self_identifier__. This can be added to group_vars/<device_role> if we want to override
the one specified in the default. folder of the role wireguard-common. 

__NB__: The following configurations are just examples. 

```yaml
wireguard_gateway-1_peer:
  endpoint_v4_public: X.X.X.X
  range_v4:
    - 10.0.0.3/32
    - 192.168.2.0/24
  wireguard_port: "51820"

wireguard_gateway-2_peer:
  endpoint_v4_public: X.X.X.X
  range_v4:
    - 10.0.0.3/32
    - 192.168.2.0/24
  wireguard_port: "51820"
# post up commands to run after the interface up
  wireguard_postup:
  - iptables -t nat -A POSTROUTING -o ens3 -j MASQUERADE
  - iptables -A FORWARD -i %i -j ACCEPT
  - iptables -A FORWARD -o %i -j ACCEPT


# this is where the binding of the peer happens. 
wireguard_peering:
    - left: wireguard_gateway-1_peer
      right: wireguard_gateway-2_peer
```

## Required parameters
* __endpoint_v4_public__: This is the public IP address of the peer
* __range_v4__: This is the subnets for which the peer routes traffic for. The virtual ip address of the tunnel is obligatory. If the peer is
a gateway you can add the subnets behind the gateway that the peer routes traffic for. 

## Optional parameters:
* __wireguard_port__: This is the port that listens to wireguard connection. The default is 51820
* __wireguard_persistent_keepalive__: This is important if the connection is between a NAT-ed peer and a public peer.
* __wireguard_postup__: These are post command that we want to run after the interface comes up. 

## Unmanaged_peers
There are times when we don't want ansible to manage the peers. A prime example would be the connection between a vy0S device. 
In this case the peer has to be added as unmanaged peer like this.

# wireguard parameters

The configuration file is deployed by the __wg.conf.j2__. Here is a basic example
```ini
# local node info
[Interface]
Address 10.0.0.1/32
PrivateKey = .....
ListenPort = 51820

# remote peer info
[Peer]
PublicKey = ....
AllowedIPs = 10.0.0.1/32, 192.168.1.0/32
Endpoint = X.X.X.X:51820
```

Most of the parameters are pretty straight forward, while others not so much. This is the case with __Address__ and 
__AllowedIPs__. 

__Address__: This parameter defined what address range the local node route traffic for. This could just be a simple
client in that case it routes traffic only for itself. It could also be bounce server that's relaying traffic to 
multiple clients. In this case the field can contain multiple subnets that the node routes traffic for. 

Ex:
Single client
```
Address = 10.0.0.1/32
```
Node is a gateway or bounce server
```
Address = 10.0.0.1/32, 192.168.2.0/24 ....
```
As we can see here we first defined the node's IP in the tunnel and the list of network the nodes route traffic for. 

__AllowedIPs__: This defines the IP range for which a peer will route traffic for. In the case of simple clients,
this is usually the vpn address. For Gateways this would be a range of IPs or subnets that the node routes traffic for. 

The examples are similar to the ones given in the __Address__ parameter. 


