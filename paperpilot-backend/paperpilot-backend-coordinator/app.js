var ShareDB = require("sharedb");
var WebSocket = require("ws");
var WebSocketStream = require("websocket-push-stream");

var redisUrl = process.env.REDIS_URL || "localhost:6379";
var mongoUrl = process.env.MONGO_URL || "localhost";

var RedisClient = require("redis").createClient({url: redisUrl});
RedisClient.on("error", function (err) {
  console.log("Error " + err);
});


var redisPubsub = require('sharedb-redis-pubsub')({client: RedisClient});
const db = require('sharedb-mongo')(mongoUrl);
var otJson = require("ot-json1");
// ShareDB 可以支持多种 OT 类型，例如 JSON 文本，普通文本，富文本等
// 具体文档可以查看 https://github.com/ottypes/docs
// 这里使用普通文本类型 ot-text
ShareDB.types.register(otJson.type);

var backend = new ShareDB({
  db: db,  // db would be your mongo db or other storage location
  pubsub: redisPubsub
});

var port = process.argv.indexOf('--port') !== -1 ? process.argv[process.argv.indexOf('--port') + 1] : 8000

// 监听端口
var wss = new WebSocket.Server({ port: port }, () => {
  console.log(`WebSocket Server Created at ${port}.`);
});

// 监听新的客户端 WebSocket 链接，对新的链接进行封装，交给 ShareDB 处理
wss.on("connection", function (ws) {
  // ShareDB 使用 stream 来与客户端实现通信，从而可以忽略底层的传输方式
  // 这里使用 WebSocket 作为底层的传输方式，保证实时数据传输
  let stream = new WebSocketStream(ws);
  // ShareDB 的前后端通信的数据以 JSON 格式传输
  // 服务端收到数据后，需要将数据从 JSON 转换为 Object
  // 并通过放入 stream 的缓存区 (push)，交给 ShareDB 处理
  ws.on("message", function (msg) {
    // 可以在这里对 msg 进行筛选，自定义的数据可以另行处理，不交给 ShareDB 处理
    console.log(JSON.parse(msg));
    stream.push(JSON.parse(msg));
  });
  // 使 ShareDB 监听新的链接
  backend.listen(stream);
});