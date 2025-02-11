# mahjong-game
一个基于Python和Pygame开发的四川麻将游戏。


## 工作流程：
    git pull origin main
    git add .
    git commit -m "初始提交"
    git push -u origin main
## 推荐流程
    - git fetch origin（1.获取远程更新不修改本地文件）
    - git diff main origin/main（2.查看差异）
    - git rebase origin/main（3.合并远程分支（推荐使用 rebase））
    - git add .（4.修改冲突文件后执行）
    - git rebase --continue
    - git push origin main（5.推送更新）

## 功能特点

- 支持单人对战AI
- 实现了基本的麻将规则和流程
- 包含碰牌等基本玩法
- 可调整窗口大小
- 动画效果流畅

## 技术栈

- Python 3.x
- Pygame
- 面向对象编程

## 运行说明

1. 确保已安装Python和Pygame
2. 在mahjong_tiles目录下放入麻将牌图片
3. 运行0211test.py启动游戏

## 待优化

- 增加更多玩法(如吃牌、杠牌等)
- 完善AI策略
- 添加音效
- 优化界面UI
