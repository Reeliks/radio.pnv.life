telnet = settings.server.telnet
telnet.set(true)
telnet.port.set(1234)
telnet.bind_addr.set("0.0.0.0")

music = mksafe(playlist(
    "/audio/music/", 
    mode="randomize", 
    reload_mode="watch",
    id="music"))

news_queue = request.queue(id="news")

def smart_transition(previous, next)
    previous_is_music = source.id(previous) == "music"
    next_is_music = source.id(next) == "music"
    if previous_is_music and next_is_music then
        add(normalize=false, [
            fade.out(duration=1.5, previous),
            fade.in(duration=1.5, next)
        ])
    else
        sequence([previous, next])
    end
end

radio = rotate(
    transitions=[smart_transition], 
    weights=[2, 2],
    [news_queue, music]
)

output.icecast(
    %mp3(bitrate=192, samplerate=44100, stereo=true),
    mount="/stream.mp3",
    host="icecast",
    port=8000,
    password=environment.get("PASSWORD"),
    name="radio.pnv.life",
    description="Some cool music playing there",
    url="https://radio.pnv.life",
    genre="Music",
    radio
)