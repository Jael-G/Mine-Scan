"""
Functions to send result information to a Discord server webhook
"""
import requests

class WebhookManager:
    def __init__(self, webhook_url):
        self.webhook_url = webhook_url

    def send_results(self, ip_range: str | tuple[str, str], total: int, hits: int, misses: int, hit_list: list[dict]) -> int:
        """_summary_

        Args:
            ip_range (str | tuple[str, str]): Single IP, CIDR or lower and upper range
            total (int): Total IPs scanned
            hits (int): IPs with server
            misses (int): Non-server IPs
            hit_list (list[dict]): Server data list

        Returns:
            int: Response status code
        """        
        json_embed: dict = self.build_embed_json(ip_range, total, hits, misses, hit_list)
        response = requests.post(self.webhook_url, json=json_embed)

        return response.status_code
    
    def build_embed_json(self, ip_range: str | tuple[str, str], total: int, hits: int, misses: int, hit_list: list[dict]) -> dict[str]:
        """_summary_

        Args:
            ip_range (str | tuple[str, str]): Single IP, CIDR or lower and upper range
            total (int): Total IPs scanned
            hits (int): IPs with server
            misses (int): Non-server IPs
            hit_list (list[dict]): Server data list

        Returns:
            dict[str]: Embed JSON as dict
        """        
        json_embed = {
            "content": "",
            "tts": False,
            "embeds": [
                {
                    "title": f"Scan Completed",
                    "color": 0x936542,
                    "url": "https://github.com/Jael-G/Mine-Scan",
                }
            ],
            "avatar_url": "https://github.com/Jael-G/Mine-Scan/blob/bd4ad785c8eee9d6c84b399906122a524fe0480b/images/mine_scan_whook_logo.png?raw=true",
            "username": "Mine Scan",
        }

        if type(ip_range) == str:
            description = f"\n**Scanned**: {ip_range}\n\n"
        else:
            description = f"\n**Scanned**: {ip_range[0]} - {ip_range[1]}\n\n"

        description += f"**Results**:\n\n📊 Total: **{total}**\n\n"

        if hits:
            description += f"✅ Hits: **{hits}**\n\n❌ Misses: **{misses}**"
        else:
            description += f"❌ No servers found"

        fields = []

        for hit in hit_list:
            ip = next(iter(hit))
            version = hit[ip]["version"]
            latency = hit[ip]["latency"]
            players = hit[ip]["players"]

            hit_json = {
                "name": ip,
                "value": f"Version: **{version}**\nPlayers: **{players}**\nLatency: **{latency}ms**",
            }

            fields.append(hit_json)

        json_embed["embeds"][0]["description"] = description
        json_embed["embeds"][0]["fields"] = fields

        return json_embed