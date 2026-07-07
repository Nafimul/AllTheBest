export async function sendFormToApi(formData, url, method) {
    try {
        const response = await fetch(url,
                                    {
                                        method: method,
                                        body: formData
                                    });
        if (!response.ok)
            return null;

        return await response.json();
    } catch (error) {
        return null;
    }
}

export async function postVote(categoryName, thingName)
{
    const formData = new FormData();
    formData.append("categoryName", categoryName);
    formData.append("thingName", thingName);
    const success = await sendFormToApi(formData, "/api/vote", "POST");
    return success;
}

export async function getThingJson(thingName)
{
f     try {
        const response = await fetch("/api/thing/" + encodeURIComponent(thingName),
                                    {
                                        method: "GET",
                                    });
        if (!response.ok)
            return null;

        return await response.json();
    } catch (error) {
        return null;
    }
}

export async function getCategoryJson(categoryName)
{
    try {
        const response = await fetch("/api/category/" + encodeURIComponent(categoryName),
                                    {
                                        method: "GET",
                                    });
        if (!response.ok)
            return null;

        return await response.json();
    } catch (error) {
        return null;
    }
}

export async function deleteVote(categoryName)
{
    const formData = new FormData();
    formData.append("categoryName", categoryName);
    formData.append("thingName", "doesn't matter");
    const success = await sendFormToApi(formData, "/api/vote", "DELETE");
    return success;
}