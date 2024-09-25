func main() {
	res, err := http.Get("http://example.com")
	if err != nil {
		//
	}
	defer res.Body.Close()

	if res.StatusCode != http.StatusOK {
		//
	}
}