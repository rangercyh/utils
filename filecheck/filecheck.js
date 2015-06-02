var reg = /[^\w\d_]/ig;
var fileList = {};
var wrongFile = [];
var wrongDir = [];
var bigFile = [];
var sameFile = [];
var totalFile = 0;
var fileSize = 0;
var fileType = {};
var maxFileList = [];
var ungryFile = [];
var beaut = {
	'.ExportJson': 1,
	'.plist': 1,
	'.png': 1,
	'.json': 1,
	'.fnt': 1,
	'.ttf': 1,
	'.fsh': 1,
	'.vsh': 1,
	'.tmx': 1
}

var fs = require('fs');
var path = require('path');
var crypto = require('crypto');

function md5(str) {
	var md5sum = crypto.createHash('md5');
	md5sum.update(str);
	return md5sum.digest('hex');
}

function reg_check(name) {
	if (reg.test(path.basename(name, path.extname(name)))) {
		return true;
	}
	return false;
}

function walk(dir) {
	var dirList = fs.readdirSync(dir),
		temp;
	dirList.forEach(function(item) {
		temp = dir + '/' + item;
		var states = fs.statSync(temp);
		if (states.isDirectory()) {
			if (reg_check(item)) {
				wrongDir.push(path.relative(process.cwd(), temp));
			}
			walk(temp);
		} else {
			var relPath = path.relative(process.cwd(), temp);
			var ext = path.extname(relPath);
			var basename = path.basename(relPath, ext);
			if (basename === 'filecheck') {
				return;
			}
			if (reg_check(item)) {
				wrongFile.push(relPath);
			}
			++totalFile;
			var data = fs.readFileSync(temp);
			var dataMd5 = md5(data);
			for (var fullPath in fileList) {
				if (fileList[fullPath] === dataMd5) {
					sameFile.push([fullPath, relPath]);
					sameFile.push(' ');
				}
			}
			if (states.size > 512 * 1024) {
				bigFile.push(relPath);
			}

			if (!fileType[ext]) {
				fileType[ext] = 0;
			}
			fileSize = fileSize + states.size;
			++fileType[ext];
			if (!beaut.hasOwnProperty(ext)) {
				ungryFile.push(relPath);
			}
			maxFileList.push([states.size, relPath]);
			fileList[relPath] = dataMd5;
		}
	});
}

walk(path.resolve(process.cwd()));
console.log('本检查只允许文件或文件夹名使用字母、数字和下划线');
console.log('文件数量 = ', totalFile);
console.log('文件总大小 = ', (fileSize / 1024 / 1024).toFixed(2), 'M');
console.log('错误文件 = ', wrongFile.length);
console.log(wrongFile);
console.log('错误文件夹 = ', wrongDir.length);
console.log(wrongDir);
console.log('相同文件：');
console.log(sameFile);
console.log('奇怪的文件：');
console.log(ungryFile);
console.log('文件类型统计：');
console.log(fileType);
console.log('超过512K的资源：');
console.log(bigFile);
maxFileList.sort(function(a, b) {
	if (a[0] == b[0]) {
		return 0;
	} else {
		return b[0] - a[0];
	}
});
console.log('前10个最大的文件：');
for (var i = 0; i < 10; ++i) {
	console.log((maxFileList[i][0] / 1024).toFixed(2), 'K', maxFileList[i][1]);
}

