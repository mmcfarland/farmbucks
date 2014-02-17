# -*- mode: ruby -*-
# vi: set ft=ruby :

# Vagrantfile API/syntax version. Don't touch unless you know what you're doing!
VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
   # Every Vagrant virtual environment requires a box to build off of.
   config.vm.box = "precise32"
   config.vm.network :forwarded_port, guest: 80, host: 8080
   config.vm.network :private_network, ip: "192.168.100.3"

   config.vm.provision "ansible" do |ansible|
      ansible.playbook = "build/site.yml"
      ansible.inventory_path = "build/hosts"
      ansible.sudo = true
   end  

end
