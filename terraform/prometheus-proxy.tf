# this file deploys a VM in GCP in accordance with the terraform workspace. It also creates a static ip for the
# VM and opens the port 22(ssh) and 9090 (prometheus) in the firewall(vpc network).
# The VM has to be added to netbox after being deployed by terraform. Please read the README of the role prometheus-proxy role.

variable "machine_type" {
  type = string
  default     = "e2-medium"
  description = "Machine  type"
}

variable "disk_image" {
  type = string
  default = "ubuntu-os-cloud/ubuntu-2004-lts"
  description = "Disk image"
}


variable "proxy-servers" {
  default = 1
  description = "Amount of proxy servers"
}

#create a static ip address for the VM.
resource "google_compute_address" "static" {
  name = "proxy-address-${terraform.workspace}"
}
resource "google_compute_instance" "prometheus-proxy" {
  count        = var.proxy-servers
  name         = "prometheus-proxy-${terraform.workspace}-${count.index+1}"
  machine_type = var.machine_type
  zone         = var.projects_data[terraform.workspace].location

  boot_disk {
    initialize_params {
      image = var.disk_image
    }
  }
  allow_stopping_for_update = true
  metadata = {
    # adds the ssh keys of releng-it members
    ssh-keys = join("\n", concat(split(",", join("\n", [for user in local.releng-it-members :
    "root:${file("${local.ssh_member_folder}/${user}")}"])),
    split(",", join("\n", [for user in local.robot-members : "root:${file("${local.ssh_robot_folder}/${user}")}"]))))
  }

  tags = ["prometheus-proxy", terraform.workspace]
  network_interface {
    network = google_compute_network.vpc.self_link
    subnetwork = "scality-subnet-releng-it-${terraform.workspace}"
    access_config {
      nat_ip = google_compute_address.static.address
    }
  }
}

resource "google_compute_firewall" "proxy-security-group" {
  name = "prometheus-proxy-${terraform.workspace}-security-group"
  network = google_compute_network.vpc.self_link
  allow {
    protocol = "tcp"
    ports = ["22", "9090"]
  }
  source_ranges = ["0.0.0.0/0"]
  target_tags = ["prometheus-proxy"]
}

