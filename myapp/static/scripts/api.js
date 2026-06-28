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
