webhook=$1
while true
do
    tmux new-session -d -s ngrok_session 'ngrok tcp 22 --log=stdout > ngrok.log'
    sleep 60
    message=$(cat ngrok.log | grep url=tcp:// | cut -d'=' -f 8)
    curl -X POST --data '{"content": "'$message'"}' --header "Content-Type:application/json" $webhook
    tmux kill-session -t ngrok_session
done