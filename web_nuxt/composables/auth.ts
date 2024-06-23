
const getHeader = async () => {
    const formData = new FormData()

    formData.append("username", "")
    formData.append("password", "")
    formData.append("scope", "")

    

    const { data: dataAuth, error: errorAuth} = await useVirty("/api/auth",{ body: formData, method: "POST" })
    if (dataAuth.value){
        let header: HeadersInit = {
            Authorization: "Bearer " + dataAuth.value.access_token
        }
        return header
    } else {
        let header: HeadersInit = {}
        return header
    }
}

export default getHeader