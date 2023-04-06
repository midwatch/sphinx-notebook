# -*- mode: ruby -*-
# vi: set ft=ruby :

HOME = ENV["HOME"]
DEV_ROOT = File.expand_path("..", Dir.pwd)

Vagrant.configure("2") do |config|
  config.vm.box = "ubuntu/focal64"

  config.vm.hostname = "sphinx-notebook"

  config.vm.provision "file", source: "#{DEV_ROOT}/.config/scm/gitconfig",
                              destination: ".gitconfig",
                              run: "always"

  config.vm.provision "file", source: "#{DEV_ROOT}/.config/env-tokens",
                              destination: "/vagrant/.env-tokens",
                              run: "always"

  config.vm.provision "file", source: "#{HOME}/.config/git/credentials",
                              destination: "/home/vagrant/.config/git/",
                              run: "always"

  config.vm.provision "shell", path: "bin/vagrant_provision.sh"
  config.vm.provision "shell", path: "bin/vagrant_provision_user.sh", privileged: false
end
