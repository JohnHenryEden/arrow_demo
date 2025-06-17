using HTTP
# websocket server is very similar to client usage
HTTP.WebSockets.listen("0.0.0.0", 8080) do ws
    for msg in ws
        # simple echo server
        HTTP.send(ws, msg)
    end
end