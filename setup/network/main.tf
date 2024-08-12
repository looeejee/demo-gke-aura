# main.tf

# Define the provider
provider "google" {
  project = "pro-lattice-432114-n5"
  region  = "us-central1"
  credentials = file("<PATH_TO_YOUR_CREDENTIALS_JSON_FILE>")
}

# Create a VPC network
resource "google_compute_network" "vpc_network" {
  name                    = "my-demo-vpc-network"
  auto_create_subnetworks = false
}

# Create a subnet within the VPC network
resource "google_compute_subnetwork" "subnet" {
  name          = "my-demo-subnet"
  ip_cidr_range = "10.0.0.0/24"
  region        = "us-central1"
  network       = google_compute_network.vpc_network.id
}

# Optional: Outputs
output "network_name" {
  value = google_compute_network.vpc_network.name
}

output "subnet_name" {
  value = google_compute_subnetwork.subnet.name
}
