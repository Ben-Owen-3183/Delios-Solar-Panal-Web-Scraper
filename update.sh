git stash
git pull 
sudo systemctl restart nginx
sudo systemctl restart solar_scraper.service



yellow='\e[0;33m'
white='\e[0;37m'

echo "\nrun the commands: "
echo -e "\t${yellow}sudo systemctl status nginx"
echo -e "${white}and"
echo -e "\t${yellow}sudo systemctl status solar_scraper.service"
echo -e "${white}to ensure both are active"