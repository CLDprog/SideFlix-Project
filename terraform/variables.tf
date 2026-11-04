# Variables adapted from TD 4.2; actual values belong in ignored terraform.tfvars.
variable "organization_name" {
  description = "First part of the account identifier before the hyphen, e.g. ABCDEFG"
  type        = string
}

variable "account_name" {
  description = "Second part of the account identifier after the hyphen, e.g. XY12345"
  type        = string
}

variable "user" {
  description = "Snowflake user associated with the RSA public key (key-pair authentication, TD 2)"
  type        = string
}

variable "private_key_path" {
  description = "Local rsa_key.p8 path outside the repository. Never commit the key."
  type        = string
}
