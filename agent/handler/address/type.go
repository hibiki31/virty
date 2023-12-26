package address

type Address []struct {
	Ifindex   int      `json:"ifindex"`
	Ifname    string   `json:"ifname"`
	Flags     []string `json:"flags"`
	Mtu       int      `json:"mtu"`
	Qdisc     string   `json:"qdisc"`
	Operstate string   `json:"operstate"`
	Group     string   `json:"group"`
	Txqlen    int      `json:"txqlen,omitempty"`
	LinkType  string   `json:"link_type"`
	Address   string   `json:"address,omitempty"`
	Broadcast string   `json:"broadcast,omitempty"`
	AddrInfo  []struct {
		Family            string `json:"family"`
		Local             string `json:"local"`
		Prefixlen         int    `json:"prefixlen"`
		Scope             string `json:"scope"`
		Label             string `json:"label,omitempty"`
		ValidLifeTime     int64  `json:"valid_life_time"`
		PreferredLifeTime int64  `json:"preferred_life_time"`
		Broadcast         string `json:"broadcast,omitempty"`
	} `json:"addr_info"`
	Altnames    []string `json:"altnames,omitempty"`
	Master      string   `json:"master,omitempty"`
	LinkIndex   int      `json:"link_index,omitempty"`
	LinkNetnsid int      `json:"link_netnsid,omitempty"`
}

type AddressIP struct {
	Local string
}
