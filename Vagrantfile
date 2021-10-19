# -*- mode: ruby -*-
# vi: set ft=ruby :

HOME = ENV["HOME"]

Vagrant.configure("2") do |config|
  config.vm.box = "ubuntu/focal64"

  config.ssh.forward_agent = true
  config.vm.hostname = "sphinx-notebook"
  config.vm.provision "file", source: "#{HOME}/.gitconfig",
                              destination: ".gitconfig",
                              run: "always"
  config.vm.provision "file", source: "#{HOME}/.config/pip/pypi-token.sh",
                              destination: "$HOME/config/pypi-token.sh",
                              run: "always"

  config.vm.provision "shell", path: "bin/vagrant_provision.sh"
  config.vm.provision "shell", path: "bin/vagrant_provision_user.sh", privileged: false
end
