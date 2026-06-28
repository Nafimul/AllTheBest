export async function postFormToApi(formData, url) {
    try {
        const response = await fetch(url,
                                    {
                                        method: 'POST',
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
    const success = await postFormToApi(formData, "/api/vote");
    return success;
}