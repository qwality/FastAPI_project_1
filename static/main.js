htmx.defineExtension('my-ext', {
    onEvent : function(name, evt) {
      if(name == 'htmx:beforeSend'){
        const token = localStorage.getItem('access_token')
        evt.detail.requestConfig.headers['Authorization'] = 'Bearer ' + token;
        console.log("Fired event: " + name, evt.detail.requestConfig.headers);
      }
    }
})
htmx.defineExtension('my-ext2', {
onEvent : function(name, evt) {
    if(name){
    console.log("Fired event: " + name, evt);
    }
}
})

$(document).ready(() => {
    $("#ajax_button").click(async function(e) {
        var accessToken = localStorage.getItem('access_token'); // Získání access_token z local storage
        $.ajax({
            url: '/user/me',
            type: 'GET',
            dataType: 'json',
            headers: {
                'Authorization': 'Bearer ' + accessToken
            },
            success: (data) => console.log('Data získána:', data),
            error: (error) => console.error('Chyba při načítání dat:', error)
        });
    });
    $('#login-form').submit(async function(e) {
        e.preventDefault();
        var formData = $(this).serialize();
        $.ajax({
            url: '/token',
            method: 'POST',
            data: formData,
            success: (response) => {
                localStorage.setItem('access_token', response.access_token)
                alert(response.access_token);
            },
            error: (error) => console.error('Chyba při požadavku:', error)
        });
    });
});

async function getUserData() {
    const token = localStorage.getItem('access_token');
    if (token) {
        const headers = { 'Authorization': `Bearer ${token}` };
        const response = await fetch('/user/me/', {
            method: 'GET',
            headers: headers
        });
        const data = await response.json();
        document.getElementById('nadpis_1').innerText = data.user_data;
    } else {
        console.error('Chybí autorizační token.');
    }
}