function FindProxyForURL(url, host) {
	if (shExpMatch(url, "*granbluefantasy.akamaized.net/*")) {
		return "PROXY 127.0.0.1:8899; DIRECT"
		//return "PROXY 127.0.0.1:8080";
	}
	return "DIRECT"
}
