import discord
import cloudscraper
import bs4
from datetime import date
import json
from discord.ext import tasks
with open('data.json') as f:
   incidents = json.load(f)
client = discord.Client()
incident_ids = []
incident_kills = {}
for incident in incidents:
    incident = incidents[incident]
    incident_ids.append(incident["Incident ID"])
    incident_kills[incident["Incident ID"]] = incident["Killed"]
print(incident_ids)
@tasks.loop(seconds = 120)
async def update():
    global incidents
    incidents_check = {}
    scraper = cloudscraper.create_scraper()
    req = scraper.get("https://www.gunviolencearchive.org/reports/mass-shooting?sort=desc&order=Incident%20Date")
    print(req.text)
    soup = bs4.BeautifulSoup(req.text, "html.parser")
    tr = soup.find_all("tr")
    inc = 0
    for a in tr:
        inc += 1
        b = a.find_all("td")
        if len(b) > 0:
            incidents_check[str(inc)] = {"Incident ID": b[0].get_text(), "Incident Date": b[1].get_text(), "State": b[2].get_text(), "City/County": b[3].get_text(), "Address": b[4].get_text(), "Killed": b[5].get_text(), "Injured": b[6].get_text(), "Source": b[7].find_all("a")[1]["href"]}
    for incident in incidents_check:
        incident = incidents_check[incident]
        if incident["Incident ID"] in incident_kills:
            old_kills = incident_kills[incident["Incident ID"]]
            new_kills = incident["Killed"]
            amt = int(new_kills) - int(old_kills)
            if (int(new_kills) - int(old_kills)) > 0:
                print("INJURED PERSON SUCCUMBED TO INJURIES")
                ctx = client.get_channel(int(912146557690855477)) #put discord channel id here
                embed=discord.Embed(title="Update on {}, {} Mass Shooting".format(incident["City/County"], incident["State"]), color=0xff0f0f)
                embed.add_field(name="Change", value="{} {} succumbed to their injuries, ({} deaths total now)".format(str(amt), (amt > 1 and "people" or "person"), str(new_kills)), inline=True)
                embed.add_field(name="Incident Date", value=incident["Incident Date"], inline=True)
                embed.add_field(name="State", value=incident["State"], inline=True)
                embed.add_field(name="City/County", value=incident["City/County"], inline=True)
                embed.add_field(name="Death Of Death", value=date.today().strftime("%B %d, %Y"), inline=True)
                embed.add_field(name="Address", value=incident["Address"], inline=True)
                embed.add_field(name="Source", value=incident["Source"], inline=True)
                await ctx.send(embed=embed)
                with open('data.json', 'w') as f:
                    json.dump(incidents_check, f)
                incidents = incidents_check
                incident_kills[incident["Incident ID"]] = new_kills
        if incident["Incident ID"] not in incident_ids:
            print("NEW SHOOTING")
            ctx = client.get_channel(int(912146557690855477))
            print(ctx, type(ctx))
            embed=discord.Embed(title="New Mass Shooting in {}, {}".format(incident["City/County"], incident["State"]), color=0xff0f0f)
            embed.add_field(name="Incident Date", value=incident["Incident Date"], inline=True)
            embed.add_field(name="State", value=incident["State"], inline=True)
            embed.add_field(name="City/County", value=incident["City/County"], inline=True)
            embed.add_field(name="Address", value=incident["Address"], inline=True)
            embed.add_field(name="Killed", value=incident["Killed"], inline=True)
            embed.add_field(name="Injured", value=incident["Injured"], inline=True)
            embed.add_field(name="Source", value=incident["Source"], inline=True)
            await ctx.send(embed=embed)
            with open('data.json', 'w') as f:
                json.dump(incidents_check, f)
            incidents = incidents_check
            incident_ids.append(incident["Incident ID"])
@client.event
async def on_ready():
    print('Logged in as {0.user}'.format(client))
    update.start()

client.run("DISCORDBOTTOKEN")
