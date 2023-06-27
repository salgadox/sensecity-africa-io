terraform {
  cloud {
    organization = "exaf-epfl"
    workspaces {
      name = "sensecity-africa-io-stage"
    }
  }
}
