function FindProxyForURL(url, host) {
	// http://prd-game-a1-granbluefantasy.akamaized.net/assets_en/img/sp/assets/npc/my/3040305000_01.png

	if (shExpMatch(url, "*granbluefantasy.akamaized.net/*")) {
		return "PROXY 127.0.0.1:8899; DIRECT"
		//return "PROXY 127.0.0.1:8080";
	} else if (shExpMatch(url, "*game.granbluefantasy.jp/*") &&
		!shExpMatch(url, "*game.granbluefantasy.jp/(authentication|ob/r)*")) {
		return "PROXY 127.0.0.1:8899; DIRECT"
		//return "PROXY 127.0.0.1:8080";
	}
	return "DIRECT"
}
