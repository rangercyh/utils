var fs = require('fs');
var path = require('path');
var crypto = require('crypto');
var execFile = require('child_process').execFile;
var version = require('./version.json');

function md5(str) {
	var md5sum = crypto.createHash('md5');
	md5sum.update(str);
	return md5sum.digest('hex');
}

var filemap = {};
function loadUsedfile() {
	var list;
	for (var key in version) {
		if (key !== 'newVersion' && version[key].update !== version.newVersion) {
			var exists = fs.existsSync(path.resolve(process.cwd(), 'filelist' + version[key].update + '.json'));
			if (exists) {
				list = require('./filelist' + version[key].update + '.json');
				for (var name in list.filelist) {
					filemap[name] = 1;
				}
			}
		}
	}
}

var Obj = {};
Obj.filenum = 0;
Obj.filelist = {};
var num = 0;
var assetsPath = path.resolve(process.cwd(), 'assets');
var newListname = path.resolve(process.cwd(), 'filelist' + version.newVersion + '.json');
fs.open(newListname, 'w', function(err, fd) {
	if (!err) {
		loadUsedfile();
		fs.readFile(path.resolve(process.cwd(), 'filehash'), function(err, data) {
			if (!err) {
				var lines = data.toString().split('\r');
				for (var i = 0; i < lines.length; ++i) {
					var l = lines[i].split('\t');

					if (l.length === 3) {
						var hashName = l[0];
						var path = l[1];
						var contentMd5 = l[2];
						var type = 'A';
						if (filemap.hasOwnProperty(hashName)) {
							// Update
							type = 'U';
						}
						Obj.filelist[hashName] = {'md5': contentMd5, 'type': type, 'name': path.slice(path.lastIndexOf('/') + 1)};
						++num;
					}
				}
			}
			Obj.filenum = num;
			fs.writeSync(fd, JSON.stringify(Obj));
			fs.closeSync(fd);
		});
	}
});
