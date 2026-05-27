echo "Please enter your router admin name: "
read name
echo "Please enter the password for $name: "
read -s password
python main.py $name $password
exit 0
