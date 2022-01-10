function ping(user) {
  var sendinfo = {
      user: user
  };
  $.post('/ping/', sendinfo, function (result) {
      console.log("/ping");
      console.log(result);
      if (! result.success) {
        // If the server do not pong, redirect to /
        window.location.href = "/";
      }
  })
}
