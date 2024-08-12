provider "google" {
  credentials = file("../../key-file.json")
  project     = "pro-lattice-432114-n5"
  region      = "us-central1"
}

resource "google_container_cluster" "primary" {
  name     = "demo-gke-aura"
  location = "europe-west1-b"  # You can choose a specific zone within the region

  initial_node_count = 1

  node_config {
    machine_type = "e2-medium"  # Choose an appropriate machine type
    oauth_scopes = [
      "https://www.googleapis.com/auth/cloud-platform",
    ]
  }

}

output "cluster_name" {
  value = google_container_cluster.primary.name
}

output "cluster_location" {
  value = google_container_cluster.primary.location
}