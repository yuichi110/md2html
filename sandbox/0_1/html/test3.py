text = '''<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="description" content="Sample Description">
    <link rel="icon" href="./assets/favicon.ico">
    <title>Sample Title</title>
    <meta name="pdfkit-page-size" content="A4"/>

  </head>

  <body>

<!-- GENERATED HTML START -->
 <h2>
 前書き
</h2>
<p>
 本書は私がシスコシステムズという会社で働いていた際に提供していた社内トレーニングの資料、
及びそれがマイナビニュースで連載となった際の記事にもとづいて書かれています。
シスコはIT業界において有名な会社であるため知っているかたも多いと思いますが、
開発というよりネットワークの会社です(USやインドの開発部隊は除く)。
つまり、本書のベースとなったトレーニングはITインフラのプロ(当然ながらプログラマーではない)に対して作られたものであるため、
他のプログラミングの専門書が飛ばしてしまったり難解に説明したりしているプログラミングの概念をかなり丁寧に説明しています。
本書を通してプログラミングがどのようなものか理解していただき、コードを書くことに抵抗がなくなって頂ければ幸いです。
なお、本書は前編・中編・後編の Python3 シリーズの前編となり、プログラミングの基礎を丁寧に説明することに注力しています。
オブジェクト指向の詳細やその他レベルの高い話題はそれほど深く扱わず、それらは本書の続編で扱います。
</p>
<p>
 プログラミングは建築にたとえることができます。たとえば犬小屋を作ろうと思ったとき、
木の柱や板を調達して適当にデザインして組み立てることができます。
構造力学の計算をするどころか、建築について素人であっても作れます。
ただ、犬小屋を作るには「犬小屋とはこういうものだ」ということと、ノコギリとハンマーの使い方は知っている必要があります。
プログラミングもこれと同じで、比較的「小さい」プログラムはノコギリやハンマーに相当する最低限の文法と
「作りたいものの仕組みをどう実現するか」ということさえ知っていれば、そこそこ動くものを作ることができます。
しかし、人が住む家を作るとなると、犬小屋とは話が変わってきます。
頑丈であり住みやすい家を作るには、まず「家というものの仕組み」を犬小屋よりも深いレベルで知っている必要があります。
なおかつ家の工作に必要となるスキルは犬小屋より高度なものとなります。
ビルの建設などになってくるとさらに高度な知識が必要になります。
プログラミングも、単に文法や「言語や設計の思想」だけでなく周辺知識のようなものを身につけていないと、
数千、数万行レベルのコードを1人で書いたり、プロジェクトを回したりすることは難しいと思います。
より大きく複雑なものを作る場合ほど、より深いレベルの知識が必要になってきます。
</p>
<p>
 まずは犬小屋を作るために、ハンマーやノコギリの使い方を正しく覚える。それがずばり本書の目的です。
</p>
<p>
 <img alt="image" class="img-responsive" src="/Users/yuichi/Git/md2x/sandbox/0_1/html/005_image/01.png"/>
</p>
<p>
 ハンマーやノコギリの使い方を座学だけで学んで、「私はハンマーとノコギリを使えます」といったら、大工さんに笑われてしまいます。
使い方は教科書でも学べますが、使いこなそうと思うと、実際に木を切って、釘を打たないと、
そのスキルは身につきません。使ってみてはじめてわかることも多いはずです。
プログラミングも本で座学するだけでなく、実際にコードを書いて、動かすことで上達します。
ゆっくりでもいいので、実際に手を動かしながら本を読み進めていってもらえれば幸いです。
</p>
<div class="codehilite">
 <pre><span></span><span class="kn">import</span> <span class="nn">os</span>

<span class="n">a</span> <span class="o">=</span> <span class="p">[</span><span class="mi">1</span><span class="p">,</span><span class="mi">2</span><span class="p">,</span><span class="mi">3</span><span class="p">,</span><span class="mi">4</span><span class="p">,</span><span class="mi">5</span><span class="p">]</span>
<span class="k">for</span> <span class="n">i</span> <span class="ow">in</span> <span class="n">a</span><span class="p">:</span>
  <span class="k">print</span><span class="p">(</span><span class="n">i</span><span class="p">)</span>
</pre>
</div>
<!-- GENERATED HTML END -->

  </body>

</html>'''

import pdfkit
#pdfkit.from_url("http://google.com", "out.pdf")

options = {
    'page-size': 'A4',
    'margin-top': '0.1in',
    'margin-right': '0.1in',
    'margin-bottom': '0.1in',
    'margin-left': '0.1in',
    'encoding': "UTF-8",
    'no-outline': None,
    'dpi':512
}

css = '/Users/yuichi/Git/md2x/sandbox/0_1/pdf/style.css'
pdfkit.from_string(text, 'test_output.pdf', options=options, css=css)
