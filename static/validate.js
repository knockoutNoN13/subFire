function validateForm() {
var name = document.forms['addForm']["nameS"].value;
var ports = document.forms['addForm']["portsS"].value;
var config = document.forms['addForm']["configS"].value;
if (name == "" || ports == "" || config == "" || config == "configs/") {
alert("Please input full configuration for service");
return false;
}
} 
