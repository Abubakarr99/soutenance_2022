Prometheus proxy
=========

Description
==========
The prometheus proxy role prometheus on a device. The device is meant to be a proxy that scrapes devices that can not be 
reached by the principal prometheus deployment. This is known as Prometheus Federation. 

Prerequisites
=============
* The Infrastructure should have already been deployed by terraform to GCP. Navigate to the GCP console under the 
right project to virtual machines and grab the IP address and name of the VM. This is important when adding the device to Netbox. 

* Before running the role, the prometheus proxy device has to be added to Netbox.
  * __Required characteristic__
    * site
    * cluster
    * tags: __environment(devl, stag or prod), ansible, monitoring-proxy__
    * Under __local config context data__ add the group of devices(device_roles) you want to be monitored by the proxy in a list form.
```json
{
  "monitored_device_groups": [
    "vpn-access-gateway",
    "hypervisor"
  ]
}
```
  * Add the interface of the device as well the ip address. The device is a VM so add the static ip address and make it the primary ip.
* The devices that are to be monitored by the proxy are to be tagged __monitored_by_proxy__. 



Validation
==========
* Navigate to the [prometheusUrl](http://x.x.x.x:9090) of the prometheus proxy and see the list of targets. This can only be accessed through the 
Scality VPN. The list of targets should be visible under __Status > Targets__ 

* Under [PrometheusPrincipal](https://x.x.x.x/prometheus/targets), the prometheus should be visible under the 
endpoint __prometheus-proxy-exporter__. 
* Query the [PrometheusPrincipal](https://x.x.x.x/prometheus/graph) for the targets monitored by
the prometheus proxy. Ex up{monitored_by="proxy"}
