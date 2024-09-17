# 第七章 函数与特殊函数  

函数是一个在自然科学、工程技术，甚至在某些社会科学中被广泛应用的数学概念，无论在初等数学还是高等数学中，无论在基础课还是专业课中，大家都会经常与函数打交道，以函数为基本工具解决各种各样的数学问题和专业问题。然而，从严格意义角度给函数下个定义并不是一件容易的事情。有人会说，函数不就是一个集合到另外一个集合的映射吗？或者说，函数就是对于某个集合中的任一元素，在另外一个集合中存在唯一元素与之对应。这不就是函数的定义？如果函数是这样定义的话，那么映射或对应又怎么定义呢？这正是函数定义的困难所在。事实上，自函数概念首次被德国数学家被莱布尼茨提出以来，其定义一直没有得到很好地解决，因为没有人能够准确地回答什么叫映射或者对应。直到在集合论和关系理论出现后，人们才以关系理论为工具完美地解决了函数的定义。具体地说，函数就是一种满足单值性要求的特殊二元关系。通过关系模型定义函数，就用关系模型的特性来诠释映射或对应概念的含义。作为关系模型的一个具体应用，本章将从特殊关系的角度来介绍函数的基本知识及其应用，包括函数的基本概念、函数的基本运算，以及若干重要的特殊函数，例如特征函数、散列函数和置换函数等。  

## $\pmb{\S7.1}$ 函数的基本概念  

函数概念的来源可以一直追溯到伟大的意大利物理家、天文学家和哲学家伽利略，伽利略在十七世纪就观察到了两个变量之间的制约关系，并用文字和比例的语言表达变量之间的函数关系。笛卡尔在他的解析几何中，已注意到一个变量对另一个变量的依赖关系，但未意识到要提炼函数概念，直到后来莱布尼茨第一个使用函数一词来表示一个量，并将函数值的变化看成是曲线上一个点的运动，才真正诞生函数的概念。人们通常使用的函数符号$f(x)$由欧拉发明。值得一提的是，欧拉是目前世界上最多产的数学家，其数学成果在他去世50 年后才基本上整理完成，但直到现在还没有全部整理完成。  

函数是数学中一个非常重要的内容,既是沟通各种学科之间的桥梁，也是读者今后学习其它相关课程的重要基础。函数方法是实际问题求解的一个基本方法论，在遇到实际问题的时候，很多情况下可以使用函数知识构造出相关的函数模型,进而通过对函数问题的研究实现对实际问题的求解。例如，深度学习中构造分类器的基本策略就是建立一个函数模型并通过数据训练使得该函数模型不断逼近所求的分类器函数。本节主要从集合与关系的角度介绍函数的基本概念，包括函数的集合定义、函数的基本类型和一些常用的特殊函数。  

### 7.1.1 函数的集合定义  

在初等数学或高等数学中，函数的概念从变量角度提出，而且主要局限于在实数集。计算机相关领域处理的对象除了实数之外，还有很多其它对象，例如矩阵、向量、命题等等，而且主要面对的是各种可数的离散对象。为此，需要扩展初等数学或高等数学中函数概念的含义，从集合与关系的角度给函数下一个更加本质性的定义，具体如下：  

【定义7.1】设$𝐴$和$B$是任意两个非空集合，$f$是从$𝐴$到$B$的关系。若对$\forall x\in A$都存在唯一的$y\in B$，满足$\langle x,y\rangle\in f$，则称关系$f$为从$𝐴$到$B$的函数关系，简称为函数或映射,记为 $f\!:\!A\longrightarrow$  

$B$或$y=f(x)$，并称$x$为$f$的自变量或源点，$𝑦$为$ x$在$f$下的函数值或像点。集合$𝐴$称为$𝑓$的定义域，记为$dom$ $f=A$，所有像点组成的集合称为$f$的值域或$f$的像，记为$ran $$f$或$f(A)$。  

从上述定义可以看出，函数$f$是从集合$𝐴$到$B$的一种特殊二元关系，这种二元关系所包含序偶的第一元素为自变量，第二元素为因变量或函数值。函数的定义域就是关系的前域$𝐴$，要求关系中所有序偶的第一元素互不相同并且要取遍集合$𝐴$中的每个元素。作为刻画作为函数的本质单值特征，要求对于关系中的任意两个序偶，若它们的第一元素相同，则第二元素必须相同。具体地说，如果一个从集合$𝐴$到$B$二元关系$f$，那么它必须满足如下几个性质：  

(1)$\langle x,y\rangle\in f\Leftrightarrow y=f(x);\qquad\mathrm{(2)}\ \langle x,y\rangle\in f\wedge\langle x,z\rangle\in f\Rightarrow y=z;$ 

（3）$|f|=|A|$； （4）$f(x)$表示一个变值，$f$代表一个集合，故$f\neq f(x)$  

如果关系$f$具备下面两种情况之一，那么$f$就不是函数关系： 

（1）存在元素$a\in A$,在$B$中没有像；（2）存在元素$a\in A$, 在$ B$中至少有两个像。 

例如，关系$\begin{array}{r}{F_{1}=\{\langle x_{1},y_{1}\rangle,\langle x_{2},y_{1}\rangle,\langle x_{3},y_{2}\rangle,\langle x_{4},y_{3}\rangle\}}\end{array}$是函数，而如下关系：  
$$
F_{2}=\{\langle x_{1},y_{1}\rangle,\langle x_{2},y_{1}\rangle,\langle x_{3},y_{2}\rangle,\langle x_{1},y_{2}\rangle\}
$$

则不是函数，因为同时有$\langle x_{1},y_{1}\rangle\in F_{2}$和$\langle x_{1},y_{2}\rangle\in F_{2}$  

【例题7.1】设集合$ A=\{1,\!2,\!3,\!4\}$和$\boldsymbol{B}=\{a,b,c,d\}$，判断下列$𝐴$到$B$的二元关系是函数关系，哪些不是，对于函数关系写出函数的值域。  

$(1) f_{1}=\{\langle1,a\rangle,\langle2,a\rangle,\langle3,d\rangle,\langle4,c\rangle\};\quad(2) f_{2}=\{\langle1,a\rangle,\langle2,a\rangle,\langle2,d\rangle,\langle4,c\rangle\};\\(3) f_{3}=\{\langle1,a\rangle,\langle2,b\rangle,\langle3,d\rangle,\langle4,c\rangle\};\quad(4) f_{4}=\{\langle1,a\rangle,\langle2,b\rangle,\langle2,c\rangle,\langle3,d\rangle,\langle4,c\rangle\};\\(5) f_{5}=\{\langle2,a\rangle,\langle2,b\rangle,\langle2,c\rangle,\langle2,d\rangle,\langle3,b\rangle,\langle4,c\rangle\};\quad(6) f_{6}=\{\langle1,a\rangle,\langle2,b\rangle,\langle3,a\rangle,\langle4,b\rangle\}$。  

【分析】根据函数定义，对集合$𝐴$中每一元素在$B$中有唯一像。据此判定是否为函数。  

【解】（1）$f_{1}$是函数关系， $f_{1}(A)=\{a,c,d\}$； 

（2）$f_{2}$不是函数关系，因为3 没有像， 2 与同时$a$和$d$对应，不满足像的单值性； 

（3）$f_{3}$是函数关系， $f_{3}(A)=\{a,b,c,d\}$； 

（4）$f_{4}$不是函数关系，因为2 同时与$c$和$d$对应，不满足像的单值性； 

（5）$f_{5}$不是函数关系，因为1 没有像，2 同时与$a,b,c,d$对应，不满足像的单值性；  

（6）$f_{6}$是函数， $f_{6}(A)=\{a,b\}$。  

【例题7.2】对于集合$A=\{1,\!2,\!3\}$到$B=\{a,b,c\}$关系$f=\{\langle1,a\rangle,\langle2,b\rangle,\langle3,c\rangle\}$和$g=$$\{\langle1,b\rangle,\langle2,b\rangle,\langle3,a\rangle\}$，判断$f,g,f\cup g,f\cap g,f-g,\bar{f},f\oplus g$是否为$𝐴$到$B$的函数。  

【分析】根据函数的定义进行判定。  

【解】根据函数的定义，$f$和$g$都是集合$A$到集合$B$的函数。 $f\cup g=\{\langle1,a\rangle,\langle2,b\rangle,\langle3,c\rangle,\langle1,b\rangle,\langle3,a\rangle\}$不是$A$到$B$的函数，因为元素1 和3 都不满足像点的单值性要求。

 $f\cap g=\{\langle2,b\rangle\}$不是$𝐴$到$B$的函数，因为元素1 和元素3 没有像点。

 $f-g=\{\langle1,a\rangle,\langle3,c\rangle\}$不是$𝐴$到$B$的函数，因为元素2 没有像点。 $\bar{f}=\{\langle1,b\rangle,\langle1,c\rangle,\langle2,a\rangle,\langle2,c\rangle,\langle3,a\rangle,\langle3,b\rangle\}$不是$𝐴$到$B$的函数, 因为元素1,2 和3 都不满足像点的单值性要求。  

$f\oplus g=\{\langle1,a\rangle,\langle3,c\rangle,\langle1,b\rangle,\langle3,a\rangle\}$不是$𝐴$到$B$的函数, 因为元素1 和3 都不满足唯一像点的单值性要求,且元素2 没有像点。  

由上述例题可知，函数作为一种特殊关系或特殊集合，其集合运算的结果可能不再是函数。因此，要慎用函数的集合运算。另一方面，由于函数是一种特殊子集，因此可用集合相等的概念来定义两个函数相等，具体定义如下：  

【定义7.2】设$𝐴$和$B$是任意两个非空集合，$f,g$是两个从$A$到$B$的函数关系，如果$f$和$g$相互包含，即有$f\subseteq g\wedge g\subseteq f$，则称函数$f$和函数$g$相等，记为$f=g$。换句话说，如果$dom $$f=$$dom$ $g$且对$\forall x\in\mathsf{d o m}$ $f=\mathrm{dom}$ $g$有$f(x)=g(x)$，称$f$与$g$相等。  

从上述定义可以看出，两个函数相等不仅要求它们的对应关系相等，而且要求它们的定义域也要相同，两者缺一不可。  

【例题7.3】判断下列函数是否相同：  

$(1)f=\{\langle x,y\rangle|x,y\in R\land y=(x^{2}-1)/(x+1)\};\,\,\,g=\{\langle x,y\rangle|x,y\in R\land y=x-1\}\,$ $(\mathrm{2})f=\{\langle x,y\rangle|x,y\in R\land y=1\};\;\;g=\{\langle x,y\rangle|x,y\in R\land y=x^{0}\}\,。$$(3)\,f=\{\langle x,y\rangle|x,y\in R\land y=x^{2}/x\};\quad g=\{\langle x,y\rangle|x,y\in R\land y=x\}\,$。 $(4)f=\{\langle x,y\rangle|x,y\in R\land y=(x^{2}+1)/x\};\quad g=\{\langle x,y\rangle|x,y\in R\land y=x+1/x\}.$  

【分析】根据函数的对应关系和定义域是否相同进行判断。  

【解】（1）、（2）、（3）由于$dom$ $f$与$dom$ $g$不相同，故它们均不是相同的函数，（4）由于$dom$ $f={dom}\ g$，且两者的对应关系相等，故它们是相同的函数。 

既然函数是一种二元关系，那么就可以用关系图来表示有限集合上的函数。例如对于集合$A=\left\{\begin{array}{r l r}\end{array}\right.$小张,小王, 小陈}，$B=\left\{\begin{array}{r l r}\end{array}\right.$博士,硕士, 本科,高中}，令：  

$$
f=\{\langle\text{小张},\text{本科}\rangle,\langle\text{小王},\text{硕士}\rangle,\langle\text{小陈},\text{博士}\rangle\}
$$

则该函数可以用关系图表示，如图所示。  

![](images/0f56c530a60991db7ab203aa16f7260fe580c9b19d557bf8eaa511fc220473fd.jpg)  
图 7-1 函数关系图表示  

从图中可以看出，定义域$𝐴$中每个元素是且仅是每个有向边的起点。图中每个有向边可以共享终点，但不能共享起点。  

现考察有限集合上函数的计数问题，即算出有限集合上有多少种不同函数。设集合$ A=$$\{a_{1},a_{2},\cdots,a_{n}\}$，$B=\{b_{1},b_{2},\cdots,b_{m}\}$，则要确定一个从$𝐴$到$B$的函数$ f$，就必须对$𝐴$中每个元素$a_{i}$，在$B$中找到一个唯一确定的元素$b_{m_{i}}$与之对应。显然，对于$𝐴$中每个元素$a_{i}$都有$|B|=m$种选择$b_{m_{i}}$的方式。而集合𝐴中共有$|A|=n$个元素，故根据乘法原理，得到所有方式的组合数为$m^{n}$或$|B|^{|A|}$种。即从$A$到$B$的不同函数一共有$|B|^{|A|}$种。由此得到如下定理：  

【定理7.1】设$𝐴$和$B$是任意两个非空有限集合，则从$A$到$B$一共有$|B|^{|A|}$种不同的函数。  

【证明】类似于前面的分析，在此从略。

 根据上述定理，可得到如下函数集定义及其表示方法：  

【定义7.3】设$𝐴$和$B$是任意两个非空集合，将从$A$到$B$的一切函数构成的集合称为从$𝐴$到$B$的函数集或函数空间，记为$B^{A}$。即有： $B^{A}=\{f|f\colon\ A\to B\}.$。  

根据上述定义，当$𝐴$和$B$是非空有限集合时，显然有：$|B^{A}|=|B|^{|A|}$

【例题7.4】假设$A=\{a,b,c\}$, $B=\{\alpha,\beta\}$,求$B^{A}$  

【解】由于$ A\times B=\{\langle a,\alpha\rangle,\langle a,\beta\rangle,\langle b,\alpha\rangle,\langle b,\beta\rangle,\langle c,\alpha\rangle,\langle c,\beta\rangle\}$，故$|A\times B|=6$，从而$A\times B$共有$2^{6}=64$个不同子集合，即共有64不同的关系。但是其中能构成函数的关系只有$|B|^{|A|}=$$2^{3}=8$种，具体如下：  

$$
f_{0}=\{\langle a,\alpha\rangle,\langle b,\alpha\rangle,\langle c,\alpha\rangle\};\;\;f_{1}=\{\langle a,\alpha\rangle,\langle b,\alpha\rangle,\langle c,\beta\rangle\};\nonumber
$$

$$
\quad\quad\quad\quad f_{2}=\{\langle a,\alpha\rangle,\langle b,\beta\rangle,\langle c,\alpha\rangle\};\,\,\,f_{3}=\{\langle a,\alpha\rangle,\langle b,\beta\rangle,\langle c,\beta\rangle\}
$$

$$
\quad f_{4}=\{\langle a,\beta\rangle,\langle b,\alpha\rangle,\langle c,\alpha\rangle\};\,\,\,f_{5}=\{\langle a,\beta\rangle,\langle b,\alpha\rangle,\langle c,\beta\rangle\}
$$

$$
f_{6}=\{\langle a,\beta\rangle,\langle b,\beta\rangle,\langle c,\alpha\rangle\};\;\;f_{7}=\{\langle a,\beta\rangle,\langle b,\beta\rangle,\langle c,\beta\rangle\}
$$

以上8 个函数即为所求，即有$B^{A}=\{f_{0},f_{1},f_{2},f_{3},f_{4},f_{5},f_{6},f_{7}\}$。

通过以上分析不难发现，当𝐴和$B$为有限集时，函数和一般关系具有以下区别：  

（1）个数差异：从$𝐴$到$B$的不同关系有$2^{|A|\times|B|}$个，从$A$到$B$的不同函数仅有$|B|^{|A|}$个。 

（2）基数不同：每个函数基数均为$|A|$即$|f|=|A|$，关系的基数却为从0 到$\vert A\vert\times\vert B\vert$

（3）第一元素的差别：关系的第一个元素可以相同，函数的第一个元素不能相同。 

下面进一步考察函数对定义域子集的映射性质，首先给出如下子集像的相关概念：  

【定义7.4】设$𝐴$和$B$是任意给定的两个非空集合，$A_{1}$和$B_{1}$分别是$𝐴$和$B$的任意两个非空子集合，即有$A_{1}\subseteq A,B_{1}\subseteq B$。$f$是一个从$𝐴$和$B$函数，即$f\colon A\to B$。  

（1）令$f(A_{1})=\{f(x)|x\in A_{1}\}$，称$f(A_{1})$为$|A_{1}$在$f$下的像。当$A_{1}=A$时，$f(A)$为$f$的像。

（2）令$ f^{-1}(B_{1})=\{x|x\in A\Lambda f(x)\in B_{1}\}$，称$f^{-1}(B_{1})$为$B_{1}$在$f$下的完全原像。 

在上述定义中显然有：$f(A_{1})\subseteq B$且$f^{-1}(B_{1})\subseteq A$。  

【例题7.5】设𝑓:$\mathbf{N}\rightarrow\mathbf{N}$，且有：  

$$
f(x)=\begin{cases}x/2&,x\text{为偶数}\\x+1&,x\text{为奇数}\end{cases}
$$

令$A=\{1,\!2,\!3\}$，$B=\{2\}$，试计算$f(A)$和$f^{-1}(B)$。

【解】根据子集像和子集完全原像的定义，有：  
$$
f(A)=\{f(1),f(2),f(3)\}=\{1,2,4\}
$$

$$
f^{-1}(B)=f^{-1}(\{2\})=\{x|x\in\mathbb{N}\land f(x)=2\}=\{1,4\}
$$

下面定理给出了子集像的集合运算性质：  

【定理7.2】设$𝐴$和$B$是任意给定的两个非空集合，$X$和$𝑌$是集合$ A$的任意两个非空子集，即有$X\subseteq A,Y\subseteq A$。$f$是一个从$A$和$B$函数，即$f\colon A\to B$。则有：  

$$
(1)f(X\cup Y)=f(X)\cup f(Y);\ \ (2)\ \,f(X\cap Y)\subseteq f(X)\cap f(Y)
$$

【证明】（1）对任意的$y$，有：  

$$
\begin{array}{r l}&{\quad y\in f(A\cup B)\Leftrightarrow\exists x(x\in A\cup B\land f(x)=y)}\\ &{\Leftrightarrow\exists x((x\in A\lor x\in B)\land f(x)=y)}\\ &{\quad\Leftrightarrow\exists x(x\in A\land f(x)=y)\lor\exists x(x\in B\land f(x)=y)}\\ &{\Leftrightarrow y\in f(A)\lor y\in f(B)\Leftrightarrow y\in f(A)\cup f(B)}\end{array}
$$

故有：$f(A\cup B)=f(A)\cup f(B)\,.$  

（2）对任意的$y$，有：  

$$
y\in f(A\cap B)\Leftrightarrow\exists x(x\in A\cap B\land f(x)=y)\Leftrightarrow\exists x((x\in A\land x\in B)\land f(x)
$$

$$
\begin{array}{r l}&{=y)}\\ &{\Rightarrow\exists x(x\in A\land f(x)=y)\land\exists x(x\in B\land f(x)=y)\Leftrightarrow y\in f(A)\land y\in f(B)}\\ &{\Leftrightarrow y\in f(A)\cap f(B)}\end{array}
$$

故有： $f(A\cap B)\subseteq f(A)\cap f(B)$ 。证毕 !    

上述定理的第（2）结论等号不成立。  

事实上，设$A=\{a,b,c\}$，$B=\{1,\!2,\!3\}$，$f\colon X\to Y$为：$f(a)=1$，$f(b)=f(c)=2.$令$X=\{a,b\}$，$Y=\{c\}$，则有：$A\cap B=\emptyset$，$f(A\cap B)=\emptyset$。但是：  

$$
f(A)\ \cap f(B)=\{1,2\}\cap\{2\}\neq\emptyset
$$

故$f(A)\ \cap f(B)\ \neq f(A\cap B)$。这表明只能成立：$f(A\cap B)\subseteq f(A)\cap f(B)\,。$  

至此，我们从二元关系的角度给了函数相关概念的本质定义，并以关系模型为基本工具分析讨论了函数的若干基本性质，为函数理论奠定了一个比较坚实的数学基础。下面就从以上函数概念及基本性质为出发点进一步介绍和讨论函数的相关理论及应用。  

### 7.1.2 函数的基本类型  

从本质上讲，从集合$𝐴$到集合$B$的函数描述的是$𝐴$中元素与$𝐵$中元素之间的一种特殊对应关系，这种特殊对应关系可以是一对一的也可以是多对一的，但不能是一对多或多对多的关系。这是函数对应关系与一般对应关系的主要差别。此外，函数值域可以是$B$的某个真子集，也可以是$B$自身。根据以上讨论，就可将所有函数分成如下四种不同的基本类型，即是单射但不是满射的函数、是满射但不是单射的函数、既是单射又是满射的函数、既不是单射也不是满射的函数。本节主要讨论这四种函数，首先给出单射函数和满射函数的定义：  

【定义7.5】设$f$从集合$𝐴$到集合$ B$的函数：  

（1）若$f$的不同自变量映射到不同的像，则称$f$为为$𝐴$到$B$的单射函数,简称为单射。也就是说，对任意的$x_{1},x_{2}\in A$，如果$x_{1}\neq x_{2}$，那么$f(x_{1})\neq f(x_{2})$，则称$f$为$𝐴$到$B$的单射。 

（2）如果集合$ B$中的每个元素都有原像，则称$f$为$𝐴$到$B$的满射函数，简称为满射；也就是说，如果$f$的值域等于$B$，即有$𝑟𝑎𝑛$ $f=B$，则称${f}$为$𝐴$到$B$的满射。

 （3）若$f$是满射且是单射，则称$f$为$𝐴$到$B$的双射；若$A=B$，则称${f}$为$𝐴$上的函数；当$𝐴$上的函数$f$是双射时，则称$f$为$𝐴$上的一个变换。  

可依据上述定义判断函数$f\colon A\to B$是否为满射、单射、双射。判断满射就是检查$B$中的每个元素是否都是函数值。如果在$B$中找到不是函数值的元素，那么$f$就不是满射的。判断单射的方法就是检查不同的自变量是否对应于不同的函数值。  

【例题7.6】设$A=B=R$（实数集），试判断下列函数的类型：  

$$
(1)f_{1}=\{\langle x,x^{2}\rangle|x\in R\};\;\;(\,2\,)\;\;f_{2}=\{\langle x,x+1\rangle|x\in R\};\;\;(\,3\,)\;\;f_{3}=\{\langle x,e^{x}\rangle|x\in R\}。
$$

【分析】在（1）中，因为$\pm x$都对应$\ x^{2}$，所以$f_{1}$不是单射，又因为$B$集合中的负实数没有原像，所以$f_{1}$不是满射，因此$f_{1}$既不是单射也不是满射；在（2）中，$f_{2}$既是单射，又是满射，即$f_{2}$是双射；在（3）中，对$\forall x_{1},x_{2}\in R$，当$x_{1}\neq x_{2}$时，$f_{3}(x_{1})\neq f_{3}(x_{2})$，所以$f_{3}$是单射，又因为$B$集合中的负实数没有原像，所以$f_{3}$不是满射，故$f_{3}$是单射。  

【解】（1）$f_{1}$为既不是单射也不是满射的函数；（2）$f_{2}$是双射；（3）$f_{3}$是单射。  

【例题7.7】确定下列函数的类型。 

（1）设$A=\{1,\!2,\!3,\!4,\!5\}$，$B=\{a,b,c,d,e\}$。$f\colon A\to B$定义为$\{\langle1,a\rangle,\langle2,c\rangle,\langle3,b\rangle,\langle4,a\rangle,\langle5,d\rangle\}。$

（2）设$A=\{1,\!2,\!3\}$，$B=\{a,b,c,d\}$。$f\!:\!A\rightarrow B$定义为$\{\langle1,a\rangle,\langle2,c\rangle,\langle3,b\rangle\}$。 

（3）设$A=\{1,\!2,\!3\}$，$B=\{1,\!2,\!3\}$。$f\!:\!A\rightarrow B$定义为$\{\langle1,2\rangle,\langle2,1\rangle,\langle3,3\rangle\}。$  

【分析】（1）对任意$\mathbf y\in B$，都存在$x\in B$，使得$\langle x,y\rangle\in f$，所以$f$是满射；但元素1 和4的像都是$a$，故$f$不是单射。综上可知$f$是满射但不是双射。  

$(2)A$中不同的元素对应不同的像，因此$f$是单射；另一方面，存在元素$d\in B$没有原像，故$f$不是满射。综上可知$f$是单射但不是满射。  

（3）$𝐴$中不同的元素对应不同的像，所以$f$是单射。又由于$B$中的每个元素都有原像，所以$f$是满射。从而$f$是双射。又因为$\boldsymbol{\lvert A=B}$，所以$f$还是变换。  

【解】（1）因为对任意$\mathbf{{y}}\in B$，都存在$x\in B$，使得$\langle x,y\rangle\in f$,所以$f$是满射。  

(2）因为$𝐴$中不同的元素对应不同的像，所以$f$是单射。

(3）因为$f$既是单射，又是满射，所以$f$是双射。又因为$A=B$，所以$f$还是变换。  

由定义7.2 和例7.1.7 可看出，若$ f$是从有限集$𝐴$到有限集$B$的函数，则$f$是单射的必要条件是$|A|\leq|B|$；$f$是满射的必要条件是$|A|\geq|B|$；$f$是双射的必要条件是$|A|=|B|$。此外，当$A$ 和$B$ 是基数相同的有限集合时，还有以下结论：  

【定理7.3】设$𝐴$，$B$是有限集合且$|A|=|B|$。如果$f$是一个从$A$到$B$的单射函数，则$f$必然是从𝐴到$B$的满射函数，反之亦然。  

【分析】可直接按照单射和满射的定义证明。  

【证明】假设$f$是单射，显然$f$是从$𝐴$到$f(A)$的满射，故$f$是从$𝐴$到$f(A)$的双射，因此$|A|=$$|f(A)|$，从而$|f(A)|=|B|$。由于$|f(A)|=|B|$且$f(A)\subseteq B$，故根据有限集合的性质有$f(A)=$$B$，故$f$为$𝐴$到$B$的满射，亦即$f$为$𝐴$到$B$的双射。  

反之，假设$f$是满射。对于$\forall x_{1},x_{2}\in A$且$x_{1}\neq x_{2}$，假设$f(x_{1})=f(x_{2})$，由于$f$为$𝐴$到$B$的满射，故$f$也是$A-\{x_{1}\}$到$B$的满射，故$|A-\{x_{1}\}|\geq|B|$，即$|A|-1\geq|B|$，这与$|A|=|B|$矛盾，因此$f(x_{1})\neq f(x_{2})$，故$f$为$𝐴$到$B$的单射，亦即$f$为$𝐴$到$B$的双射。  

【例题7.8】对于给定的集合构造双射函数$𝑓$:$A\rightarrow B$。 $A=P(\{1,\!2,\!3\}),~~B=\{0,\!1\}^{\{1,2,3\}};~~(\mathrm{2})~~A=Z,B=N\circ$  

【分析】构造的函数需满足既是单射又是满射。  

【解】（1） $A=\{\emptyset,\{1\},\{2\},\{3\},\{1,2\},\{1,3\},\{2,3\},\{1,2,3\}\}。$$B=\{f_{0},f_{1},\cdots,f_{n}\}$，其中：

 $\begin{array}{c c}{{f_{0}=\{\langle1,0\rangle,\langle2,0\rangle,\langle3,0\rangle\};}}&{{f_{1}=\{\langle1,0\rangle,\langle2,0\rangle,\langle3,1\rangle\};}}\\ {{f_{2}=\{\langle1,0\rangle,\langle2,1\rangle,\langle3,0\rangle\};}}&{{f_{3}=\{\langle1,0\rangle,\langle2,1\rangle,\langle3,1\rangle\};}}\\ {{f_{4}=\{\langle1,1\rangle,\langle2,0\rangle,\langle3,0\rangle\};}}&{{f_{5}=\{\langle1,1\rangle,\langle2,0\rangle,\langle3,1\rangle\};}}\\ {{f_{6}=\{\langle1,1\rangle,\langle2,1\rangle,\langle3,0\rangle\};}}&{{f_{7}=\{\langle1,1\rangle,\langle2,1\rangle,\langle3,1\rangle\}.}}\end{array}$  

令$f\colon A\to B$且满足：  

$\begin{array}{c}{{f(\emptyset)=f_{0},\;\;f(\{1\})=f_{1},\;\;f(\{2\})=f_{2},\;\;f(\{3\})=f_{3},}}\\ {{f(\{1,2\})=f_{4},\;\;f(\{1,3\})=f_{5},\;\;f(\{2,3\})=f_{66},\;\;f(\{1,2,3\})=f_{7} }}\end{array}$ 

上述$𝑓$:$A\rightarrow B$即为所求。  

(2) 如表7 −1 所示，将$𝑍$中元素表中顺序排列并与$N$中元素相对应：  

表 7-1 顺序排列并对齐 
![](images/d5210a555e58b3e825e2a3d7189f4dd91467879d0dcb587673f2bf0328add52d.jpg)  

则这种对应所表示的函数是：  

$$
f\colon Z\to N,\;\;f(x)={\left\{\begin{array}{l l}{2x}&{\qquad x\geq0}\\ {-2x-1}&{\quad x<0}\end{array}\right.}
$$

上述$f\!:\!Z\to N$即为所求。解毕！  

【例题7.9】对于有限集$A$和有限集${B}$，设$|A|=3$，$|B|=4$,计算可定义多少种不同的$𝐴$到$B$的单射函数。  

【分析】主要运用排列的原理进行计数。

 $𝐴$到$B$的单射函数数目为4 个元素中取三个的排列，即有：  
$$
P(4,3)=4!/(4-3)!=24
$$

【例7.1.10】对于有限集$𝐴$和有限集$B$，设$|A|=4$，$|B|=3$,计算可定义多少种不同的$𝐴$到$B$的满射函数。  

【分析】如果把$𝐴$中元素的两个元素“合并”，即把$𝐴$看作由3 元素组成的集合，由于由3 个元素的集合到3 个元素的集合可定义的双射函数为$3!=\!\!6$ 个，而4 个元素“合并”成3 个元素共有$\mathsf{C}(4,\!2)=6$种方案，故由乘法原理知，$A$到$B$的满射函数共有$6\cdot6=36$种。  

【解】可定义36 种不同的满射函数。

【例题7.10】设$A=\{1,2,\cdots,n\}$，$f$是从$𝐴$到$𝐴$的满射且具有性质：  
$$
\begin{array}{r}{f(x_{i})=y_{i}\;\;\;\;\;i=1,2,\cdots,k;k\leq n;x_{i},y_{i}\in A}\end{array}
$$

求$f$的个数。  

【分析】从有限集到有限集的满射也是单射，故$f$是从$𝐴$到$𝐴$的双射。将$𝐴$中的$n$个元素看成$_{,n}$个座位，在固定$k$个元素位置后，剩下的$n-k$个元素的坐法数就是$f$的个数。  

【解$\pmb{\lambda}f$是从𝐴到𝐴的满射，故$f$是从$A$到𝐴的双射。由于$\cdot f$已将𝐴中的某$k$个元素与𝐴中另外$k$个元素对应确定，故只需要考虑剩下$\,n-k$个元素的对应关系。为此，令：  

$$
B=A-\{x_{i}|i=1,2,\cdots,k\},\qquad C=A-\{y_{i}|i=1,2,\cdots,k\}
$$

则从$B$到$C$的满射个数（也就是双射个数）就是$f$的个数，故满足题目条件的不同满射个数为 $(n-k)!$   

7.1.3 常用特殊函数  

数学中常用的特殊函数有很多，在初等数学和高等数学中都有大量的分析讨论，例如三角函数、指数函数等基本初等函数，不再一一赘述。在此，我们主要介绍在计算机科学应用中经常使用的一些函数，例如恒等函数、常函数、取整函数、布尔函数、自然映射函数等。下面给出这些常用特殊函数的定义。  

【定义7.6】设$𝐴$和$B$是任意给定的两个非空集合：

 （1）设$f\colon A\to B$，若有$c\in B$，对$\forall x\in A$都有$f(x)=c$，则称$f\colon A\to B$是常函数。  

（2）$𝐴$上的恒等函数就是$𝐴$的恒等关系$I_{A}$，对$\forall x\in A$，有$I_{A}(x)=x$。 

（3）对实数 $x$ ， $f(x)$ 取不小于 $ x$ 的最小整数，则称 $f(x)$ 为上取整函数， 记为 $f(x)=\left\lceil x\right\rceil$  

（4）对实数$x$，$f(x)$取不大于$ x$的最大整数，则称$f(x)$为下取整函数，记为$f(x)=\lfloor x\rfloor$

（5）如果$f(x)$是从集合$𝐴$到$B=\{0,1\}$上的函数，则称$f(x)$为布尔函数。  

（6）设$R$是$𝐴$上的等价关系，$A/R$是$𝐴$在关系$R$上的商集，令$g\colon A\to A/R$，$g(x)=[x]_{R}$则称$g$是从$A$到$A/R$的自然映射。  

【例题7.11】设${A}={B}={R}$（实数集），试指出下列函数的类型。 $(1)f_{1}=\{\langle x,x\rangle|x\in R\};\ \mathrm{~(2)~}\,f_{2}=\{\langle x,a\rangle|x\in R,a\in R\}；$ $(3)f_{3}=\{\langle x,\lceil x\rceil\rangle|x\in R\};\ \ (\mathrm{\scriptsize~4})\ \ (4)f_{4}=\{\langle x,\lfloor x\rfloor\rangle|x\in R\}。$  

【分析】在（1）中，对$\forall x\in A$都有$f_{1}(x)=x$，故$f_{1}$是恒等函数；在（2）中，存在$x\in R$，使得对$\forall x\in A$都有$f_{2}(x)=a$，故$f_{2}$是常值函数；在（3）和（4）中，根据上取整和下取整函数的定义，容易判断它们分别是上取整函数和下取整函数。  

【解】$f_{1}$是恒等函数； $f_{2}$是常值函数； $f_{3}$是上取整函数； $f_{4}$是下取整函数。  

【例题7.12】存在计算机磁盘上的数据或网络上传输的数据通常表示为字节串,每个字节由8 个数字组成,要表示100 字位的数据需要多少字节?  

【分析】 根据题意,只需求100 除以8 的上取整函数即可。

 【解】因为$s=\lceil100/8\rceil=13$，所以表示100 字位的数据需要13 字节。  

【例题7.13】在异步传输模式下,数据按53 字节分组,每组称为一个信元,在数据传输速率为每秒500 千字位的连接上一分钟能传输多少个ATM 信元。  

【分析】 首先需要求出一分钟能传输的字位数,然后再求出这些字位数可以组成多少个信元,因为要求一分钟能够传输的信元数,故需用下取整函数完成。  

【解】因为一分钟能够传输的字节数为$500\times1000\times60/8=3750000$,所以一分钟能传输的信元数为 $\lfloor3750000/53\rfloor=70754\rfloor$ 。  

## $\pmb{\S7.2}$ 函数的基本运算  

函数的运算对于大家来说并不陌生，我们在初等数学和高等数学中都会经常使用函数运算实现问题求解。事实上，函数的运算有很多种，除了前述的加、减、乘、除等算术运算之外，还有复合运算、逆运算、积分运算、微分运算等等，这里不再一一枚举。本节主要从关系的角度介绍和考察与计算机领域密切相关的一些函数运算。如前所述，函数作为一种表示特殊二元关系的集合，其交、并、补、差运算结果不一定还是函数关系。因此，我们不再考虑函数关系的集合运算，而着重考察函数关系的复合运算、逆运算和递归运算。  

### 7.2.1 函数的复合运算  

前面已经学习了二元关系的复合运算，函数作为一种特殊的二元关系，也可以进行复合运算，函数的复合运算其实就是函数关系的合成，下面定理保证了两个函数关系的复合后得到的关系仍然是一个函数关系，并据此得到复合函数的定义：  

【定理7.4】设$f\colon A\to B,g\colon B\to C$是两个函数，则$f$与$g$的复合关系：

$f\circ g=\{\langle x,z\rangle|x\in A\wedge z\in C\wedge(\exists y)(y\in B\wedge xfy\wedge ygz)\}\quad\text{(7-1)}$

 是一个从$𝐴$到$C$的函数，称之为函数$f$与$g$的复合函数，记为$f\circ g\colon A\to C$。  

【证明】因为$f$和$g$分别是$𝐴$到$B$和$B$到$C$上的二元关系，故由复合关系的定义可知$f\circ g$是一个𝐴到$C$上二元关系。下面证明$f\circ g$是一个函数：  

对于某个$x\in\operatorname{dom}(f\circ g)$，如果存在两个元素$z_{1},z_{2}\in\mathrm{ran}(f\circ g)$，有$\langle x,z_{1}\rangle\in(f\circ g)$和$\langle x,z_{2}\rangle\in(f\circ g)$，则分别存在$y_{1},y_{2}\in B$满足：$x f y_{1}\wedge y_{1}g z_{1}$和$x f y_{2}\wedge y_{2}g z_{2}$。即有：  

$$
\langle x,y_{1}\rangle\in f,\,\langle x,y_{2}\rangle\in f;\;\;\langle y_{1},z_{1}\rangle\in g,\;\;\langle y_{2},z_{2}\rangle\in g
$$

由于$ f$是函数，根据函数的单值性有$\dot{}y_{1}=y_{2}$。同理，根据函数$g$的单值性，可由$y_{1}=y_{2}$得到$z_{1}=z_{2}$。因此，$f\circ g$是一个满足单值性的二元关系，因而是一个函数。  

根据上述定理，由于两个函数的复合运算结果仍然是一个函数，故可将函数复合运算直接推广到多个函数的情形，并且多个函数复合运算结果仍是函数。由于函数复合是关系复合的一种特殊情形，故多个函数的复合同样满足结合律。此外，从上述定理可以看出：  

（1）函数$ f$与$g$可以复合的前提条件是，前一个函数$f$的值域$ran$ $f$必须是后一个函数$g$定义域$dom$ $g$的子集合，即有：$ran $$f\subseteq\operatorname{dom}\ g=B$；  

（2）复合函数$f\circ g$的定义域$\operatorname{dom}(f\circ g)$是前一个函数$ f$的定义域$dom$ $f$，值域ran$(f\circ g)$是后一个函数$$g$$的值域，即有：$\operatorname{dom}(f\circ g)=\operatorname{dom}\ f=A,\ \operatorname{ran}(f\circ g)=r a n g;$  

（3）对$\forall x\in A$，有：$f\circ g(x)=g(f(x))。$  

【例题7.14】设集合$ A=\{a,b,c,d\},B=\{b,c,d\},C=\{a,b,d\}$，已知如下 $A$到$B$的函数$ f$与集合B到集合C的函数$g$，求复合函数$f\circ g$。  

$$
f=\{\langle a,b\rangle,\langle b,b\rangle,\langle c,d\rangle,\langle d,d\rangle\};\,\,\,g=\{\langle b,a\rangle,\langle c,d\rangle,\langle d,d\rangle\}
$$

【解】依题意有：ran $f=\{b,d\}\subseteq\{b,c,d\}=\mathsf{d o m}\ g$，故$f$与$g$可以复合，根据复合函数定义有：$f\circ g=\{\langle a,a\rangle,\langle b,a\rangle,\langle c,d\rangle,\langle d,d\rangle\}$。  

【例题7.15】对${R}$ 上函数$f(x)=2x+1$和$g(x)=x^{2}+1$，求$f\circ g,g\circ f,f\circ f,g\circ g。$【解】$f(x)$和$g(x)$显然满足复合条件，依据复合函数定义可以得到：  

$$
f\circ g(x)=g{\bigl(}f(x){\bigr)}=(2x+1)^{2}+1=4x^{2}+4x+2
$$

$$
g\circ f(x)=f{\big(}g(x){\big)}=2(x^{2}+1)+1=2x^{2}+3
$$

$$
f\circ f(x)=f{\big(}f(x){\big)}=2(2x+1)+1=4\mathrm{x}+3
$$

$$
g\circ g(x)=g{\bigl(}g(x){\bigr)}=(x^{2}+1)^{2}+1=x^{4}+2x^{2}+2\,
$$

下面定理给出了函数单射、满射和双射性质在复合运算下的保持性：

 【定理7.5】设$f\colon A\to B,g\colon B\to C$是两个函数。  

（1）如果函数$f$和$g$都是满射，则复合函数$f\circ g$也是从$A$到$C$满射； 

（2）如果函数$f$和$g$都是单射，则复合函数$f\circ g$也是从$𝐴$到$C$单射； 

（3）如果函数$f$和$g$都是双射，则复合函数$f\circ g$也是从𝐴到$C$双射。  

【证明】 （1）对于$\forall c\in C$，由于$ g$是满射，故存在∃$b\in B$,使得$g(b)=c$。对于$b\in B$,又因为$ f$是满射，故$\exists a\in A$，使得$f(a)=\ b$。从而有：  

$$
f\circ g(a)=g{\bigl(}f(a){\bigr)}=g(b)=c
$$

即存在$a\in A$，使得$f\circ g(a)=c$。因此$f\circ g$是满射。  

（2）对$\forall a_{1},a_{2}\in A$且 $a_{1}\neq a_{2}$，由$f$是单射知$f(a_{1})\neq f(a_{2})$。令$\begin{array}{r}{b_{1}=f(a_{1}),b_{2}=f(a_{2})}\end{array}$由$$g$$是单射可知：$g(b_{1})\neq g(b_{2})$,即$g(f(a_{1}))\neq g(f(a_{2}))$。从而有：  

$$
f\circ g(a_{1})\neq f\circ g(a_{2})
$$

所以$f\circ g$是单射。  

3）综合是1）、2）的结果即可得证。  

需要注意的是上述定理的逆不成立，但有以下结论： 

【定理7.6】设$f\colon A\to B,g\colon B\to C$是两个函数，则有：  

（1）如果复合函数$f\circ g$是从$𝐴$到$C$满射，则函数$g$是$B$到$C$的满射； 

（2）如果复合函数$f\circ g$是从$𝐴$到$C$单射，则函数$f$是$𝐴$是$B$的单射； 

（3）如果复合函数$f\circ g$是从$A$到$C$双射，则$f$是$A$是$B$的单射，$g$是$B$到$C$的满射。  

【分析】定理的条件和结论都与单射，满射和双射有关，故可按其定义进行证明。  

【证明】（1）对$\forall c\in C$，由于$f\circ g$是从$A$到$C$满射，故$\exists a\in A$，使得 $f\circ g(a)=g(f(a))=c$  

因为$f$是从$A$是$B$的函数，所以存在$b\in B$使得$f(a)=b$，即对$\forall c\in C$，存在$b\in B$使得$g(b)=c$。根据满射的定义知：$g$是$B$到$C$的满射。  

（2）$\forall a_{1},a_{2}\in A$且$a_{1}\neq a_{2}$。由于$f\circ g$是从$A$到$C$单射，故有： $f\circ g(a_{1})=g{\bigl(}f(a_{1}){\bigr)}\neq g{\bigl(}f(a_{2}){\bigr)}=f\circ g(a_{2})$  

因为$g$是$B$到$C$的函数，根据函数的单值性有$f(a_{1})\neq f(a_{2})$，即$f$是从$𝐴$是$B$的单射。 

（3）综合是1）、2）的结果即可得证。  

值得注意的是，在上述定理中，如果复合函数$f\circ g$是从$A$到$C$满射，可推出函数$g$是$B$到$C$的满射，但不能推出函数$f$是$A$是$B$的满射。例如，对于$A=\{a_{1},a_{2},a_{3}\},\ B=\{b_{1},b_{2},b_{3}\},\ C=$$\{c_{1},c_{2}\}$，由 $f=\{\langle a_{1},b_{1}\rangle,\langle a_{2},b_{3}\rangle,\langle a_{3},b_{2}\rangle\}$和$g=\{\langle b_{1},c_{1}\rangle,\langle b_{2},c_{2}\rangle,\langle b_{3},c_{2}\rangle\}$，可得：  

$$
f\circ g=\{\langle a_{1},c_{1}\rangle,\langle a_{2},c_{2}\rangle,\langle a_{3},c_{2}\rangle\}
$$

显然，$f\circ g$是满射函数，但$f$不是满射函数。  

同样，如果复合函数$f\circ g$是从$𝐴$到$C$单射，可推出函数$ f$是$A$是$B$的单射，但不能推出函数$g$是$B$到$C$的单射。读者可自己给出反例。  

【例题7.16】设按顺序排列的13 张红心纸牌：  

$\begin{matrix}\text{A}&2&3&4&5&6&7&8&9&10&\text{J}&\text{Q}&\text{K}\end{matrix}$

经过一次洗牌后牌的顺序变为：  

$\begin{matrix}3&8&\text{K}&\text{A}&4&10&\text{Q}&\text{J}&5&7&6&2&9\end{matrix}$

问再经两次同样方式的洗牌后牌的顺序是怎样的？  

表7-2 对应结果
![](images/45da7938c2ad7cecb82bd76879facb690090aab3c0395f199a61d21aeb588a88.jpg)  

【分析】将洗牌的过程看成建立函数$ f$的过程，即有$f(A)=3,f(2)=8,f(3)=K,f(4)=$$A,f(5)=4,f(6)=10,f(7)=\mathrm{Q},f(8)=J,f(9)=5,f(10)=7,f(J)=6,f(\mathrm{Q})=2,f(K)=9,$ 则经两次同样方式的洗牌后牌的顺序即为求$f\circ f\circ f$的值。  

【解】对应结果如表7-2 所示。  

### 7.2.2 函数的逆运算  

在一般关系$𝑅$的求逆运算中，任意关系都可进行求逆运算而得到其逆关系，但是对于任意一个函数$𝑓$来说，只能保证它的逆$f^{-1}$是一个二元关系，并不能保证$f^{-1}$一定是函数关系。因此，在求一个函数的逆运算时，必须对该函数做一些特殊的要求。  

【定义7.7】设$f\colon A\to B$的函数关系，如果其逆关系：  

$$
f^{-1}=\{\langle y,x\rangle|x\in A\land y\in B\land\langle x,y\rangle\in f\}\quad\text{(7-2)}
$$

是一个从$B$到$𝐴$的函数关系，则函数$f$可逆，并称$f^{-1}$是函数$f$的逆函数或反函数。  

由上述定义可可知，如果函数$f$可逆，则$f^{-1}$作为一个从$B$到$𝐴$的函数，集合$ B$中每个元素都有$ f^{-1}$下的像，而根据逆关系的定义，$B$中每个元素在函数$f^{-1}$下的像其实就是该元素在函数$f$下的原像，故$f$是从$𝐴$到$B$的满射。另一方面，$f^{-1}$作为一个函数，集合$ B$中每个元素都有$A$中唯一的元素与之对应。从函数$ f$的角度看，就是$𝐴$中不同的元素对应不同的像，因此，函数$f$是单射。综上所述，函数$f$存在逆函数$f^{-1}$当且仅当$f$是双射。  

【例题7.17】判断下列函数哪些存在逆函数，若存在则算出逆函数。  

（1）集合$ A=\{1,\!2,\!3\}$到$|B=\{a,b,c\}$的函数$f=\{\langle1,c\rangle,\langle2,b\rangle,\langle3,a\rangle\}$； 

（2）集合$A=\{1,\!2,\!3\}$到$|B=\{a,b,c,d\}$的函数$f=\{\langle1,a\rangle,\langle2,b\rangle,\langle3,d\rangle\}$；

（3）$h=\{\langle x,x+1\rangle|x\in Z\}$； 

(4) $g{\colon}Z\to Z,g(x)=2x+1;$ 

（5）集合$ A=\{1,\!2,\!3\}$到$B=\{a,b\}$的函数$\boldsymbol{g}=\{\langle1,a\rangle,\langle2,a\rangle,\langle3,b\rangle\}$。  

【分析】判断是否存在逆函数判断该函数是否是双射，若是，则存在逆函数，再根据逆函数的定义求解。  

【解】（1）$f$是双射，故存在逆函数且有$f^{-1}=\{\langle c,1\rangle,\langle b,2\rangle,\langle a,3\rangle\}$ ； 

（2）$f$不是双射，故不存在逆函数；

 $(\,3\,)\,h$是双射，故存在逆函数且有$h^{-1}=\{\langle x+1,x\rangle|x\in Z\}$，即$h^{-1}=\{\langle x,x-1\rangle|x\in Z\}$  

（4）对于$\langle x,2x+1\rangle\in g$，应有$<2x+1,x>\in g^{-1}$。令$2x+1=y$,可得$\boldsymbol{x}=(y-1)/2$.故$f^{-1}$不是 $Z$到𝑍的函数，所以函数$f$不存在逆函数。  

（5）$g^{-1}=\{\langle a,1\rangle,\langle a,2\rangle,\langle b,3\rangle\}$不是$B=\{a,b\}$到$A=\{1,\!2,\!3\}$的函数，故$g$不可逆。

【定理7.7】设$f\colon A\to B$的双射函数，则$f$的逆函数$f^{-1}$也是从$B$到$𝐴$的双射函数。 

【分析】证明 $f^{-1}$ 既是满射又是单射即可。  

【证明】首先证明$f^{-1}$是满射。因为ran $f^{-1}=\operatorname{dom}\ f=A$，故$f^{-1}$是从$B$到$𝐴$的满射函数。  

再证$f^{-1}$是单射，用反证法。假设对$\forall b_{1},b_{2}\in B$且 $b_{1}\neq b_{2}$，有：  

$$
f^{-1}(b_{1})=f^{-1}(b_{2})
$$

即存在$a\in A$，使得$.<b_{1},a>\in f^{-1}$且$<b_{2},a>\in f^{-1}$，即有：  

$$
\langle a,b_{1}\rangle\in f,\langle a,b_{2}\rangle\in f
$$

这与函数$f$单值性矛盾。故有$f^{-1}(b_{1})\neq f^{-1}(b_{2})$，即$f^{-1}$是从$B$到$𝐴$的单射函数。 故$f^{-1}$既是满射又是单射，即$f^{-1}$是从$B$到$A$的双射函数。

【例题7.18】设$f\!:\!R\rightarrow R$, $g\colon R\to R$，且有：  
$$
f(x)=\left\{\begin{matrix}x^2&\quad x\ge3\\-2&\quad x<3\end{matrix}\right.;\quad g(x)=x+2
$$

试求$f\circ g$和$g\circ f$，若$f$和$g$存在反函数，则求出其反函数，若不存在反函数，则说明原因。 【解】根据题意及复合函数的定义，可得：  

$$
f\circ g\colon R\to R ; f\circ g(x)=\left\{\begin{matrix}x^2+2&\quad x\geq3\\0&\quad x<3\end{matrix}\right.
$$

$$
g\circ f\colon R\to R; g\circ f(x)=\left\{\begin{matrix}(x+2)^2&&x\geq1\\-2&&&x<1\end{matrix}\right.
$$

$f\!:\!R\rightarrow R$不是双射的，故不存在反函数；  

$g\colon R\to R$是双射故存在反函数，且有：$g^{-1}$：$R\rightarrow R$，$g^{-1}(x)=x-2$ 

下面定理给出了任一双射函数与其函数反函数及恒等函数之间的关系：  

【定理7.8】设$𝑓$:$A\rightarrow B$的双射函数，则有：  

$$
(1)f^{-1}\circ f=I_{B};\mathrm{~(~2~)~}\,f\circ f^{-1}=I_{A};\mathrm{~(~3~)~}\,I_{A}\circ f=f\circ I_{B}=f。
$$

其中$I_{A}$和$I_{B}$分别表示集合$𝐴$和集合 $B$上的恒等函数。  

【证明】首先证明（1）：由于$f$是从$𝐴$到$B$的函数，$f^{-1}$是从$B$到$𝐴$的函数，故$f^{-1}\circ f$是一个从$B$到$B$的函数。对于$\forall\langle x,y\rangle\in f^{-1}\circ f$，则有$y=f(f^{-1}(x))$,根据$f^{-1}\circ f$的定义，必存在集合$𝐴$中的某个元素${u}$,满足$\langle x,u\rangle\in f^{-1}$且$\langle u,y\rangle\in f$,或写成$\langle u,x\rangle\in f$且$\langle u,y\rangle\in f$，即有：  

$$
x=f(u)\,\exists y=f(u)
$$

由于函数$f\colon A\to B$是单射，故有$x=y$，即$\langle x,y\rangle\in I_{B}$。故有$f^{-1}\circ f\subseteq I_{B}$  

反之，对于$\forall\langle x,y\rangle\in I_{B}$，则有${}x,y\in B$且$x=y$。由于$f^{-1}$是一个从$B$到$A$的函数，故根据$f^{-1}$的单值性知，必然存在$𝐴$中的某个元素$u$，使得$u=f^{-1}(x)$且$u=f^{-1}(y)$，即有：  

$$
\left\langle x,u\right\rangle\in f^{-1}\wedge\left\langle y,u\right\rangle\in f^{-1}
$$

可将上式写成$\left\langle x,u\right\rangle\in f^{-1}\wedge\left\langle u,y\right\rangle\in f$，则有$\langle x,y\rangle\in f^{-1}\circ f$。故有：$I_{B}\subseteq f^{-1}\circ f$ 。 

综合上述证明，可得：$f^{-1}\circ f=I_{B}$。  

可类似证明（2）和（3），在此从略。  

【例题7.19】假设$f$是由表7-3 定义，即$f(A)=D$, $f(B)=E$, $f(C)=S$,等等,试找出给定密文“$QAIQORSFDOOBUIPQKJBYAQ$”对应的明文。  

表7-3 明密文对照表
![](images/1c83ff6553e4738b0caaf0c9cf8fad21f5c7f213bb35860af2b5c4de1b040ac9.jpg)  

【分析】实际上,表7-3 给出了一个双射函数$f$,为了求给定密文的明文,只需求出$f$的逆函数$f^{-1}$,按照$f^{-1}$的对应关系依次还原出对应字母的原像,就可以得到该密文对应的明文。  

【解】由表7-3 知, $f^{-1}$如表7-4 所示。  

表7-4 密文还原明文
![](images/34d692b583506df31175522236a1a199ecfae338e6446cd60b877cac54b6951f.jpg)  

将密文“$QAIQORSFDOOBUIPQKJBYAQ$”中的每一个字母在$f^{-1}$中找出其对应的像,就可得到对应的明文: “$THETRUCKARRIVESTONIGHT$”。  

### 7.2.3 函数的递归运算  

前面从二元关系的角度讨论了函数关系的复合运算和逆运算，我们还可以将关系的幂运算引入函数关系之中。如前所述，关系的幂运算是一种特殊的复合运算，就是关系通过不断地与其自身进行复合从而产生新的关系。由于关系的复合运算满足结合律，故给定次数下的复合运算结果是唯一确定的。同样，一个函数关系也可以通过不断与其自身进行复合运算产生新的函数关系，由此可得函数迭代与递归运算的概念。  

【定义7.8】假设$𝐴$是任一给定的非空集合，$f(x)$是$A$上的某个函数，$n$个相同函数$f(x)$的复合运算称为对$f(x)$的$n$次迭代运算，运算结果记为$f^{n}(x)$，称为$f(x)$的$n$次迭代函数，并约定$f(x)$的0 次迭代函数为其自变量$x$，即有：  

$$
f^{(n)}(x)=f(f^{(n-1)}(x))\wedge f^{(0)}(x)\quad\text{(7-3)}
$$

其中$f^{(0)}(x)=x。$ 

迭代是函数的一个非常重要的运算，在很多情况下可使用函数迭代得到新的函数。例如，假设$f(x)$是自然数集上的后继函数，即有$f(x)=x+1$，则有$f^{(n)}(x)=~x+n$。还可以使用迭代方法解方程或方程组，例如牛顿迭代法、雅可比迭代法、高斯迭代法等等，有兴趣的读者可以数值分析的课程的相关内容，这里不再赘述。下面将函数迭代的概念做进一步推广，给出并讨论函数递归运算的概念。  

首先看一个引例。西萨·班·达依尔发明了国际象棋，国王问他需要什么奖赏，他说：“陛下，请您在这张棋盘的第1 个小格里赏给我一粒麦子，在第2 个小格里给2 粒，第3 个小格给4 粒，以后每一小格都比前一小格加一倍，直到摆满这64 个棋盘格”  

那么需要多少粒麦子呢？可以按如下方法计算：  

$$
f(1)=1;f(2)=2;f(3)=4;\cdots\cdots;f(n)=2*f(n-1)
$$

最后得到：$f(64)=2^{64-1}=18446744073709551615.$是一个非常大的数字。  

上面的算式$f(n)=2*f(n-1)$表达的就是一个递归运算。该算式采用以步长为1 的逐步推进的方式，通过以$f(n-1)$为变量的某个具体表达式计算$f(n)$。  

下面给出函数递归运算的具体定义：  

【定义7.9】对于某一函数$f(x)$，其定义域是集合$𝐴$，那么若对于$𝐴$集合中的某一个值$x_{n}$，其函数值$f(x_{n})$由以$f(x_{n-1}),f(x_{n-2}),\cdots,f(x_{n-k})$变量的某个表达式确定决定，即有：  

$$
f(x_{n})=S(f(x_{n-1}),f(x_{n-2}),\cdots,f(x_{n-k}))\quad\text{(7-4)}
$$

则称$f(x)$为一个$k$阶递归函数。  

递归函数的思想就是将复杂问题分解成若干简单且相同的子问题，将复杂的原问题转换为简单子问题的某种重复，通过简单子问题的机械重复得到复杂问题的解。  

例如，下列两个函数均为递归函数。  

（1）阶乘函数：  

$$
Fact(n)=\left\{\begin{matrix}1&&n=0\\&n*Fact(n-1)&&n>0\end{matrix}\right.
$$

（2）2 阶的Fibonacci 数列：  

$$
Fib(n)=\begin{cases}0&\quad&n=0\\1&\quad&n=1\\&\quad&Fib(n-1)+Fib(n-2)&\quad\text{否则}\end{cases}
$$

递归函数的上述思想非常符合计算机程序设计的思维方式。因此，递归方法是算法与程序设计的一个有效方法,使用递归方法能使程序变得简洁和清晰。  

值得注意的是，并不是任何函数都适合采用递归的形式进行计算。使用递归方式计算函  

数必须具备如下两个基本条件：  

（1）函数存在递归结束条件及结束时的值，称之为递归出口； 

（2）函数能够用递归形式表示，且递归向终止条件发展，称递归表达式为递归体。  

【例题7.20】小猴在某天摘了一些桃子，当天吃掉一半多一个，第二天接着吃掉剩下的一半多一个，以后每天都吃掉尚存桃子的一半多一个，第7 天早上只剩1 个，问小猴摘了多少个桃子？  

【分析】由题意知，第$n$天的桃子个数应是第$n+1$天个数加1 以后的2 倍，故可归纳出：递归体为$f(n)=(f(n+1)+1)*2$,递归出口为$f(7)=1$.  

【解】可得递归函数为：  

$$
f(n)=\left\{\begin{matrix}1&&&n=7\\&&(f(n+1)+1)\cdot2&&n<7\end{matrix}\right.
$$

使用以上递归函数便可求解：  

$$
\begin{array}{r l}&{f(6)=(f(6+1)+1)\cdot2=(f(7)+1)\cdot2=(1+1)\cdot2=4}\\ &{f(5)=(f(5+1)+1)\cdot2=(f(6)+1)\cdot2=(4+1)\cdot2=10}\\ &{f(4)=(f(4+1)+1)\cdot2=(f(5)+1)\cdot2=(10+1)\cdot2=22}\\ &{f(3)=(f(3+1)+1)\cdot2=(f(4)+1)\cdot2=(22+1)\cdot2=46}\\ &{f(2)=(f(2+1)+1)\cdot2=(f(3)+1)\cdot2=(46+1)\cdot2=94}\\ &{f(1)=(f(1+1)+1)\cdot2=(f(2)+1)\cdot2=(94+1)\cdot2=190}\end{array}
$$

因此，小猴摘了190个桃子。  

## $\pmb{\S7.3}$ 集合的特征函数  

前面我们从二元关系与集合的角度介绍和讨论函数的相关知识，包括函数的集合定义和函数的关系运算。在本节，我们考虑相反的问题，就是如何以函数为基本工具来解决集合的相关问题。具体地说，就是通过引入集合特征函数将关于集合的表示和运算转化为函数的表示和运算，将关于集合问题的求解转化为关于函数问题的求解。  

### 7.3.1 特征函数的概念  

首先，解决如何使用函数来表示集合的问题。为此，给出如下特征函数的概念：  

【定义7.10】假设$U$为任一给定的集合，对于$U$的任一子集$𝐴$特征函数$\chi_{A}$定义为一个从$U$到集合{0,1}二值函数：  

$$
\chi_{A}(a)=\left\{\!\!\begin{array}{c}{{1,~~~~~~~~~~~~~~~~~~~~~~~~~a\in A~~~}}\\ {{0,~~~~~~~~~~~~~~~~~a\in U-A~~~}}\end{array}\right.\quad\quad\quad\quad\quad(7-5)
$$

由以上定义可知，集合$U$的任意一个子集$𝐴$都有一个与之相对应的特征函数$\chi_{A}$。例如，对于集合$U=\{a,b,c\}$的子集$A=\{a\}$，则有：  

$$
\chi_{A}(a)=1\,,\,\,\,\chi_{A}(b)=0\,,\,\,\,\chi_{A}(c)\,。
$$

此外，根据特征函数定义显然有：空集的特征函数恒为0，$U$的特征函数恒为 1.即：  

$$
(1)A=\emptyset\Leftrightarrow(\forall x\in X)(\chi_{A_{1}}(x)=0);\;\;(\;2)\;\;A=U\Leftrightarrow(\forall x\in X)(\chi_{A_{1}}(x)=1)\,\mathrm{{s}}
$$

【例题7.21】$U=\{a,b,c,d\},A=\{b,c\}$，$B=\{a,b,d\}$，求$\chi_{A}$和$\chi_{B}$

【分析】根据特征函数的定义计算即可。 $【解】\chi_{A}=\{\langle a,0\rangle,\langle b,1\rangle,\langle c,1\rangle,\langle d,0\rangle\},\,\,\,\chi_{B}=\{\langle a,1\rangle,\langle b,1\rangle,\langle c,0\rangle,\langle d,1\rangle\}_{\circ}\,\,\,$  

### 7.3.2 特征函数的运算  

有了集合的特征函数之后，集合之间的关系就可以用其特征函数的关系表达，集合之间的运算就转化为其特征函数之间的运算。  

【定理7.9】给定全集$U$，$A\subseteq U$和$B\subseteq U$，则对所有$x\subseteq U$，成立下列关系式：$(1)\chi_{\bar{A}}(x)=1-\chi_{A}(x);~~(2)~~\chi_{A\cap B}(x)=\chi_{A}(x)\cdot\chi_{B}(x)=m i n\{\chi_{A}(x),\chi_{B}(x)\};$ $(3)\chi_{A\cup B}(x)=\chi_{A}(x)+\chi_{B}(x)-\chi_{A\cap B}(x)=m a x\{\chi_{A}(x),\chi_{B}(x)\};$ $(4)\chi_{A}(x)\leq\chi_{B}(x)\Leftrightarrow A\subseteq B;\;\;(5)\chi_{A}(x)=\chi_{B}(x)\Leftrightarrow A=B;$ $(6)\chi_{A-B}(x)=\chi_{A\cap\bar{B}}(x)=\chi_{A}(x)\cdot\chi_{\bar{B}}(x)=\chi_{A}(x)-\chi_{A\cap B}(x)\,。$  

【证明】（1） $\chi_{\bar{A}}(x)=1-\chi_{A}(x)$，在性质上取$B=\bar{A}$，则有$1=\chi_{A\cup B}(x)=\chi_{A}(x)+$$\chi_{\bar{A}}(x)-\chi_{\emptyset}(x)$，故$\chi_{\bar{A}}(x)=1-\chi_{A}(x)\,$。  

（2）全集$U$分为不相交的四个子集：$A\cap B,\;\;A\cap\bar{B},\;\;\bar{A}\cap B,\;\;\bar{A}\cap\bar{B}$，则有：  

$\text{若}x\in A\cap B, \text{则}\chi_{A\cup B}(x)=1, \chi_{A}(x)=1, \chi_{B}(x)=1, \chi_{A\cap B}(x)=1, \text{故有:}\\\chi_{A\cup B}(x)=\chi_{A}(x)+\chi_{B}(x)-\chi_{A\cap B}(x)$  

若$x\in A\cap B$,则$\chi_{A\cup B}(x)=1,\,\,\,\chi_{A}(x)=1,\,\,\,\chi_{B}(x)=0,\,\,\,\chi_{A\cap B}(x)=0$，故有：  

$$
\chi_{A\cup B}(x)=\chi_{A}(x)+\chi_{B}(x)-\chi_{A\cap B}(x)
$$

若$x\in\bar{A}\cap B$，则$\chi_{A\cup B}(x)=1,\,\,\,\chi_{A}(x)=0,\,\,\,\chi_{B}(x)=1,\,\,\,\chi_{A\cap B}(x)=0$，故有：  

$$
\chi_{A\cup B}(x)=\chi_{A}(x)+\chi_{B}(x)-\chi_{A\cap B}(x)
$$

若 $x\in\bar{A}\cap\bar{B}$ ，则 $\chi_{A\cup B}(x)=0,\,\,\,\chi_{A}(x)=0,\,\,\,\chi_{B}(x)=0,\,\,\,\chi_{A\cap B}(x)=0，$ $故有：\chi_{A\cup B}(x)=\chi_{A}(x)+\chi_{B}(x)-\chi_{A\cap B}(x)$  

（3）若$x\in A\cap B$，则有：  

$$
\chi_{A\cap B}(x)=1=1\cdot1=\chi_{A}(x)\cdot\chi_{B}(x)
$$

若 $x\notin A\cap B$ ， 则有 $\chi_{A\cap B}(x)=0$ 。 由于 $x\in{\bar{A}}$ 或 $x\in{\overline{{B}}}$ ， 则 $\chi_{A}(x)=0$  或 $\chi_{B}(x)=0$ 即 $\chi_{A}(x)$ ∙$\chi_{B}(x)=0$，从而有：$\chi_{A\cap B}(x)=\chi_{A}(x)\cdot\chi_{B}(x)\,$。  

（4）若 $A\subseteq B$ ，则可分为三种情况：若 $x\in A$ 且 $x\in B$ ，则有 $1=\chi_{A}(x)=\chi_{B}(x)$ ；若   $x\in$ $\bar{A}$且$x\in B$，则有${A}(x)=0<\chi_{B}(x)=1$；若 $x\in{\bar{A}}$且$x\in{\bar{B}}$，则有$0=\chi_{A}(x)=\chi_{B}(x)$。以上三种情况，均有$\chi_{A}(x)\leq\chi_{B}(x)$。  

反之，若$\chi_{A}(x)\leq\chi_{B}(x)$，对任意$x\in U$成立，往证$A\subseteq B$。假设$𝐴$不含于$ B$，从而存在$x\in$$A$且$x\notin B$，于是$\chi_{A}(x)=1$，$\chi_{B}(x)=0$，故$\chi_{A}(x)>\chi_{B}(x)$，这与前提矛盾，所以$A\subseteq B$。  

（5）是性质（4）的推论。（6）证明略。

【例题7.22】$U=\{a,b,c,d\},B=\{b,c\},\,\,\,C=\{a,b,d\},$，求$\chi_{B\cap C}$和$𝜒_{𝐵∪𝐶}$

【分析】使用特征函数的运算法则求解。  

$【解】\chi_{B}=\{\langle a,0\rangle,\langle b,1\rangle,\langle c,1\rangle,\langle d,0\rangle\},\,\,\,\chi_{C}=\{\langle a,1\rangle,\langle b,1\rangle,\langle c,0\rangle,\langle d,1\rangle\}\,$。

故有： $\chi_{B\cap C}=\{\langle b,1\rangle\}$ ； $\chi_{B\cup C}=\{\langle a,1\rangle,\langle b,1\rangle,\langle c,1\rangle,\langle d,1\rangle$ 。   

【例题7.23】下面利用集合的特征函数来证明的集合运算法则。  

（1）幂等律：$A\cup A=A;\quad A\cap A=A$ 

（2）交换律：$A\cup B=B\cup A$； $A\cap B=B\cap A$。 

（3）$A\cup B\cup C=A\cup(B\cup C);\,\,\,A\cap B\cap C=A\cap(B\cap C)\,$ 

（4）互补律：$A\cup\bar{A}=U;\;\;2)\;\;A\cap\bar{A}=\emptyset$。  

【证明】（1）仅证明第一个，根据上述运算法则可知：  

$$
\chi_{A\cup A}(x)=\mathrm{max}\{\chi_{A}(x),\chi_{A}(x)\}=\chi_{A}(x)
$$

故有：$A\cup A=A$  

（2）仅证明第二个，因为  

$$
\chi_{A\cap B}(x)=\operatorname*{min}\{\chi_{A}(x),\chi_{B}(x)\}=\operatorname*{min}\{\chi_{B}(x),\chi_{A}(x)\}\qquad\quad=\chi_{B\cap A}(x)
$$

故有：$A\cap B=B\cap A$  

（3）仅证明第一个，因为：  

$\operatorname*{max}\{\operatorname*{max}\{\chi_{A}(x),\chi_{B}(x)\}\,,\chi_{C}(x)\}=\operatorname*{max}\{\chi_{A}(x),\operatorname*{max}\{\chi_{B}(x),\chi_{C}(x)\}\}$

 即有$\chi_{A\cup B\cup C}(x)=\chi_{A\cup(B\cup C)}(x)$。故有： $A\cup B\cup C=A\cup(B\cup C)$。  

（4）仅证明第一个，因为：  

$$
\chi_{A\cup\bar{A}}(x)=\operatorname*{max}\{\chi_{A}(x),\chi_{\bar{A}}(x)\}=\operatorname*{max}\{\chi_{A}(x),1-\chi_{A}(x)\}=\left\{\!\!\!\begin{array}{c c}{\operatorname*{max}\{1,0\}}&{x\in A}\\ {\operatorname*{max}\{0,1\}}&{x\notin A}\end{array}\!\!\right.
$$

故有： $\chi_{A\cup\bar{A}}(x)=1.$  而 $\chi_{U}(x)=1$ ，所以 $\chi_{A\cup\bar{A}}(x)=\chi_{U}(x)=1.$  即 $A\cup\bar{A}=U$ 。证毕。   

读者可自己使用特征函数给出其它集合运算法则的证明。应用特征函数还可以证明一些集合恒等式。  

【例题7.24】证明$(A\cup B)-C=(A-C)\cup(B-C)$  

$\text{【证明】:}\chi_{(A-C)\cup(B-C)}(x)=\chi_{A-C}(x)+\chi_{B-C}(x)-\chi_{A-C}(x)\cdot\chi_{B-C}(x)\\=\chi_{A}(x)-\chi_{A}(x)\cdot\chi_{C}(x)+\chi_{B}(x)-\chi_{B}(x)\cdot\chi_{C}(x)\\-\chi_{A}(x)\cdot\chi_{B}(x)+\chi_{A}(x)\cdot\chi_{B}(x)\cdot\chi_{C}(x)$

$\begin{aligned}&=\chi_{A\cup B}(x)-(\chi_{A}(x)+\chi_{B}(x)-\chi_{A}(x)\cdot\chi_{B}(x))\cdot\chi_{C}(x)\\&=\chi_{A\cup B}(x)-\chi_{A\cup B}(x)\cdot\\\chi_{C}(x)&=\chi_{A\cup B-C}(x)。\end{aligned}$

根据集合特征函数与集合的对应关系，有：$(A\cup B)-C=(A-C)\cup(B-C)$。  

【例题7.25】设$U=\{a,b,c\}$的子集是：$\emptyset,\{a\},\{b\},\{c\},\{a,b\},\{a,c\},\{b,c\},\{a,b,c\}$,试给出 $U$ 的所有子集的特征函数且建立特征函数与二进制之间的对应关系。  

【解】$U$的任何子集𝐴的特征函数的值由表7-5 给出。  

表 7-5 子集特征函数 
![](images/ab1153c64f0c6845241d24fc582c3b9faf24a25d796a94cc5917c680ad606507.jpg)  

若将集合中元素次序确定下来，例如规定元素次序为$a,b,c$，则每个子集𝐴的特征函数与一个三位二进制数一一对应，例如，有：$\chi_{\{a,c\}}\leftrightarrow101$。  

令$B=\{000,\!001,\!010,\!011,\!100,\!101,\!110,\!111\}$，则表可看成是从$U$到$B$的一个双射。  

## $\S7.4$ 有限集的置换函数  

有限集上的函数是一类很特别的函数，具有很多非常重要而有趣的性质。如前所述，有限集$𝐴$上的单射必是满射，满射也必是单射。因此，有限集$𝐴$上的函数只有两种基本类型，一 种是双射函数，另外一种则为既非单射也非满射的函数。不难看出，有限集$𝐴$上双射函数其实就是$𝐴$上所有元素的一个全排列，因此，有限集$𝐴$上双射函数也称为置换函数。本节主要讨论有限集$𝐴$上双射函数的概念与关系运算性质，包括置换函数的基本概念、置换函数的运算性质、置换函数的轮换分解。  

### 7.4.1  置换函数的概念  

设$𝐴$是一个任意给定的非空有限集，由函数计数原理知，$𝐴$上所有不同双射函数个数也是有限的。因此，可将这些所有不同双射函数放在一起组成一个集合，并将该集合作为分析讨论𝐴上双射函数性质的背景或载体。为此，下面给出双射函数集的概念：  

【定义7.11】设$A=\{x_{1},x_{2},\cdots,x_{n}\}$是一个有穷集合， $𝐴$上所有的双射函数构成的集合称为𝐴上的双射函数集或可逆函数集。记为$F_{A}$。  

对于双射函数集$F_{A}$，显然有如下性质：  

$( 1) \forall f, g\in F_A\Rightarrow f\circ g\in F_A\wedge$ $g\circ f\in F_A。 ( 2)$ $\forall f, g, h\in F_A$ $\Rightarrow ( f\circ g) \circ h= f\circ ( g\circ$

$h)$。

(3) $\forall f\in F_{A}\Rightarrow f\circ I_{A}= I_{A}\circ f= f$。

(4) $\forall f\in F_{A}$ $\Rightarrow f^{- 1}\in F_{A}$

【例7.4.1】设$A=\{1,\!2,\!3\}$，求$F_{A}$，并考察$F_{A}$中元素之间的关系。  

【分析】根据可逆函数集的定义求解即可。  

【解】由定义有：  

$$
f_{1}=\left\{\langle1,1\rangle,\langle2,2\rangle,\langle3,3\rangle\right\}=I_{A};~~f_{2}=\left\{\langle1,1\rangle,\langle2,3\rangle,\langle3,2\rangle\right\}=f_{2}^{-1}
$$

$$
f_{3}=\{\langle1,2\rangle,\langle2,3\rangle,\langle3,1\rangle\}=f_{6}^{-1};\;\;f_{4}=\{\langle1,2\rangle,\langle2,1\rangle,\langle3,3\rangle\}=f_{4}^{-1}
$$

$$
{f_{5}}=\{\langle1,3\rangle,\langle2,2\rangle,\langle3,1\rangle\}={f_{5}^{-1}};~~{f_{6}}=\{\langle1,3\rangle,\langle2,1\rangle,\langle3,2\rangle\}={f_{3}^{-1}}
$$

$F_{A}$中一共有6 个函数，它们构成$\ A\;=\;\{1,2,3\}$中所有元素的全排列，其中$f_{1}$为恒等函数，每个函数都有逆函数，有的函数的逆函数就是其自身。  

考虑到有限集合$A=\{x_{1},x_{2},\cdots,x_{n}\}$的双射函数其实就是$𝐴$所有元素的全排列，为更加直观地表示这种排列形式，可将双射函数$f$表示成如下形式：  

$$
f={\binom{x_{1}}{f(x_{1})}}\quad{\begin{array}{l l l l}{x_{2}}&{x_{3}}&{\cdots}&{x_{n}}\\ {f(x_{2})}&{f(x_{2})}&{f(x_{3})}&{\cdots}&{f(x_{n})}\end{array}}\quad\text{(7-6)}
$$

例如，上例中$F_{A}$的6 个函数，可表示为：  

$$
f_{1}={\bigl(}{\begin{array}{l l l}{1}&{2}&{3}\\ {1}&{2}&{3}\end{array}}{\bigr)}\ \ ;\ \ \ f_{2}={\bigl(}{\begin{array}{l l l}{1}&{2}&{3}\\ {1}&{3}&{2}\end{array}}{\bigr)}\,;\ \ f_{3}={\bigl(}{\begin{array}{l l l}{1}&{2}&{3}\\ {2}&{3}&{1}\end{array}}{\bigr)}
$$

$$
f_{4}={\binom{1}{2}}\ \ \ {2}\ \ \ {3\atop1}\ \ ;\ \ \ f_{5}={\binom{1}{3}}\ \ \ {2}\ \ \ {3\atop2}\ ;\ \ \ f_{6}={\binom{1}{3}}\ \ \ {2}\ \ \ {3\atop1}\ \ \ {2\atop2}
$$

从效果上看，有限集合$ A=\{x_{1},x_{2},\cdots,x_{n}\}$上的全排列其实就是实现了$A$中全部元素排列次序的一个置换，由此得到如下置换函数的概念：  

【定义7.12】设$ A=\{x_{1},x_{2},\cdots,x_{n}\}$是一个有限集合，从$𝐴$到$𝐴$的双射函数称为$𝐴$上的一个置换函数，简称为置换或排列，记为$P{\mathrel{:}}A\to A$，$A$的基数$n$称为置换的阶。  

由于置换函数表示的是有限集合上元素的全排列，故通常使用字母$P$或$\pi$作为置换函数的函数名，即有：  

$P=\begin{pmatrix}x_1&x_2&x_3&&\cdots&x_n\\P(x_1)&P(x_2)&P(x_3)&&\cdots&P(x_n)\end{pmatrix}\quad(7-7)$

上式其中第一行是集合$ A$的元素按顺序列出，第二行元素是$A$中元素对应的函数值。显然序列$P(a_{1}),P(a_{2}),\cdots,P(a_{n})$是$𝐴$中元素的重排，恰好对应一个$ N=\{1,2,\cdots,n\}$全排列。  

显然有$F_{A}=\left\{f\middle|f\right.$是𝐴中的置换}，即可逆函数集是$𝐴$中所有置换的集合。由于 $n$元有限集中共有$n\,!$个不同的置换函数，故有$|F_{A}|=n!$，因此，有时亦将$𝐴$的可逆函数集记为𝐴！。  

【例题7.26】设$A=\{1,\!2,\!3\}$，试写出$𝐴$上的所有置换$P$  。

【分析】因为置换是一个双射函数,当选取$𝐴$中不同的元素时,对应的像互不相同,因为$P(1),P(2),P(3)$是1,2,3 的一个排列。1,2 和3 的全排列总数为3！,即𝐴的所有置换$P$共有6个。  

【解】$𝐴$上的所有置换$P$如下：  

$$
P_{1}={\left(\begin{array}{l l l}{1}&{2}&{3}\\ {1}&{2}&{3}\end{array}\right)}\qquad P_{2}={\left(\begin{array}{l l l}{1}&{2}&{3}\\ {1}&{3}&{2}\end{array}\right)}\qquad P_{3}={\left(\begin{array}{l l l}{1}&{2}&{3}\\ {2}&{1}&{3}\end{array}\right)}
$$

$$
P_{4}={\left(\begin{array}{l l l}{1}&{2}&{3}\\ {2}&{3}&{1}\end{array}\right)}\qquad P_{5}={\left(\begin{array}{l l l}{1}&{2}&{3}\\ {3}&{1}&{2}\end{array}\right)}\qquad P_{6}={\left(\begin{array}{l l l}{1}&{2}&{3}\\ {3}&{2}&{1}\end{array}\right)}
$$

【例7.4.4】等边三角形如图7-2 所示，求经过旋转和翻转能使之重合的所有置换函数。  

【分析】从图8.4.1 可以看出,当三角形绕中心$𝐴$反时针旋转$120^{\circ}$ $240^{\circ}$和$360^{\circ}$后,所得到的三角形与原三角形重合,三角形绕中心$A$的旋转可以用置换函数表示,例如三角形绕中心$A$反时针旋转$120^{\circ}$对应的置换函数$P_{1}$为: $P_{1}(1)=2$ $P_{1}(2)=3,P_{1}(3)=1$。同理可以得到其他旋转情况的置换函数。  

另外,当三角形分别绕中线1𝐴,2𝐴,3𝐴翻转时，所得到的三角形仍然与原三角形重合。  

![](images/dfc0ac05a966b10c9b40c32031fe75f0a3f10f9a71c73ad6ad121b639abaa310.jpg)  
图7-2 等边三角形  

【解】能使重合的置换分为旋转和翻转两种情形，具体如下：

（1）三角形绕中心$𝐴$反时针旋转$120^{\circ}$, $240^{\circ}$和$360^{\circ}$对应的3 个置换： 

$P_1=\begin{pmatrix}1&2&3\\2&3&1\end{pmatrix}, P_2=\begin{pmatrix}1&2&3\\3&1&2\end{pmatrix}, P_3=\begin{pmatrix}1&2&3\\1&2&3\end{pmatrix} $

（2）三角形分别绕中线1𝐴,2𝐴,3𝐴翻转时得到的三个置换： 

$P_4=\begin{pmatrix}1&2&3\\1&3&2\end{pmatrix}, P_5=\begin{pmatrix}1&2&3\\3&2&1\end{pmatrix},\quad P_6=\begin{pmatrix}1&2&3\\2&1&3\end{pmatrix} $

以上得到的6 个置换函数即为所求。  

上面已经介绍了可逆函数集和置换函数的概念，下面介绍置换函数的运算。  

### 7.4.2 置换函数的运算  

置换是一种特殊的双射函数，关于函数的求逆运算和复合运算在置换中完全适用。因此，可直接将一般函数的逆运算和复合运算作为置换函数的逆运算和复合运算。  

【例题7.27】求下列两个置换$\pi_{1}$, $\pi_{2}$的逆置换及复合置换，并计算${\pi_{1}}^{-1}$ ∘ ${\pi_{2}}^{-1}$ 。

$\pi_1=\begin{pmatrix}1&2&3\\1&3&2\end{pmatrix}; \pi_2=\begin{pmatrix}1&2&3\\2&3&1\end{pmatrix} $

【分析】可以将置换写成函数形式：$\pi_{1}=\{\langle1,1\rangle,\langle2,3\rangle,\langle3,2\rangle\}$ $\pi_{1}=\{\langle1,2\rangle,\langle2,3\rangle,\langle3,1\rangle\}$。然后，根据函数逆运算和复合运算定义进行运算。  

【解】将$\cdot\pi_{1}$, $\pi_{2}$写成函数关系的形式：  

$$
\pi_{1}=\{\langle1,1\rangle,\langle2,3\rangle,\langle3,2\rangle\},\;\pi_{2}=\{\langle1,2\rangle,\langle2,3\rangle,\langle3,1\rangle\}
$$

从而有：  

${\pi_{1}}^{-1}=\{\langle1,1\rangle,\langle2,3\rangle,\langle3,2\rangle\};\ \ \ \ \ P_{4}^{\ -1}=\{\langle1,2\rangle,\langle2,3\rangle,\langle3,1\rangle\};$ $\pi_{1}\circ\,\,\pi_{2}=\{\langle1,2\rangle,\langle2,1\rangle,\langle3,3\rangle\};\quad{\pi_{1}}^{-1}\circ\,\,{\pi_{2}}^{-1}=\{\langle1,3\rangle,\langle2,2\rangle,\langle3,1\rangle\}。$

解毕！  

从上例子可知，集合$𝐴$中置换函数的逆运算和复合运算结果还是$𝐴$的一个置换。从排列的角度看，置换函数的逆运算其实就是将置换的上下两排元素进行颠倒排放，即将下面一排移到上面，同时将上面一排移到下面，然后将数对按第一个元素（上面元素）的升序排列。  

虽然可以直接将一般函数的复合运算作为置换函数的复合运算，但是从排列的角度看，直接使用置换函数的复合运算会对排列的分析带来一些不便。为此，我们对置换函数的复合运算规则稍加调整，得到如下置换函数乘积运算的概念：  

【定义7.13】设$A=\{a_{1},a_{2},\cdots,a_{n}\}$的任意两个$n$阶置换函数$\pi$和$\tau$ ：

$\begin{gathered}\pi=\begin{pmatrix}a_1&a_2&a_3&\cdots&a_n\\\pi(a_1)&\pi(a_2)&\pi(a_3)&\cdots&\pi(a_n)\end{pmatrix}\\\tau=\begin{pmatrix}a_1&a_2&a_3&\cdots&a_n\\\tau(a_1)&\tau(a_2)&\tau(a_3)&\cdots&\tau(a_n)\end{pmatrix}\end{gathered}$

则$\pi$和$\tau$的乘积$\pi\cdot\tau$定义为：  

$\pi\cdot\tau=\begin{pmatrix}a_1&a_2&a_3&\cdots&a_n\\\pi(\tau(a_1))&\pi(\tau(a_2))&\pi(\tau(a_3))&\cdots&\pi(\tau(a_n))\end{pmatrix}\quad\text{(7-8)}$

在不引起混淆的情况下，通常省略乘法符号，即将$\pi\cdot\tau$简写为$\pi\tau$  

从上述定义可以看出，置换函数乘积运算与复合运算之间没有本质上的区别，只是表达形式上有所差异，具体地说，就是它们之间的运算次序正好相反，即$\pi\cdot\tau=\tau\circ\pi$。  

【例题7.28】已知：  

$\pi=\begin{pmatrix}1&2&3\\2&3&1\end{pmatrix}\text{和}\tau=\begin{pmatrix}1&2&3\\3&1&2\end{pmatrix}$

计算下列置换的乘积：（1）$\pi\tau$；（2）$\pi^{2}$；（3）$\pi\tau^{2}$。

【解】根据置换乘积运算的定义，得到：  

$\pi\tau=\begin{pmatrix}1&2&3\\2&3&1\end{pmatrix}\begin{pmatrix}1&2&3\\3&1&2\end{pmatrix}=\begin{pmatrix}1&2&3\\1&2&3\end{pmatrix};$

$\pi^2=\begin{pmatrix}1&2&3\\2&3&1\end{pmatrix}\begin{pmatrix}1&2&3\\2&3&1\end{pmatrix}=\begin{pmatrix}1&2&3\\3&1&2\end{pmatrix};$

$\pi\tau^2=(\pi\tau)\tau=\begin{pmatrix}1&2&3\\1&2&3\end{pmatrix}\begin{pmatrix}1&2&3\\3&1&2\end{pmatrix}=\tau。$

解毕！ 

### 7.4.3  置换的轮换分解  

细心的读者可能会发现，前面几个置换函数例题的排列元素都只有3 个，这是主要因为置换数目的增长速度为排列元素数目的阶乘${n!}$，如果$n$比较大，则问题的规模会迅速增大而变得不可行。因此，对于有限集合$A=\{a_{1},a_{2},\cdots,a_{n}\}$上的置换，当$n$比较大时，就必须置换进行分解。现在我们考察对置换进行分解的具体方法。  

首先考察一种特殊的置换，在这种置换中的一些元素的函数映射呈现出一种循环的状态，而其余元素则的映射为恒等映射。例如，对于如下置换：  

$\begin{pmatrix}1&2&3&4&5&6&7&8\\4&3&5&2&1&6&7&8\end{pmatrix}$

元素1 映射到4，元素4 映射到2，元素2 映射到3，元素3 映射到5，元素5 映射到1，然后循环。置换中这5 个元素1, 4, 2, 3, 5形成一个循环，而其余元素6, 7, 8则保持恒等映射，此时称这样的置换为长度为5 的轮换，记为(1, 4, 2, 3, 5),即有：

$\begin{pmatrix}1&2&3&4&5&6&7&8\\4&3&5&2&1&6&7&8\end{pmatrix}=(1,4,2,3,5)  $

轮换的具体定义如下：  

【定义7.14】设$A=\{a_{1},a_{2},\cdots,a_{n}\}$是任一非空有限集合，如果$𝐴$上的某个置换$P$把元素$a_{1}$变成$a_{2}$, $a_{2}$变成$a_{3},\ \cdots,a_{k-1}$变成$a_{k}$，又把$a_{k}$变成$a_{1}(k\leq n)$，但别的元素（如果有的话）都不变，则称$ P$是一个长度为$k$的轮换，简称为$\pmb{k}{-}$轮换，并将其记为$(a_{1},a_{2},\cdots,a_{k})$。其中长度为2 的轮换称为对换。  

由上述定义可知，轮换是置换另一种表达方式，它以元素变化次序为序，描述一种轮换过程$(a_{1},a_{2},\cdots,a_{k})=(a_{2},a_{3},\cdots,a_{k}a_{1})=\cdots=(a_{k},a_{1},\cdots,a_{k-1})。$例如对于轮换$(1,4, 2, 3, 5)$，有：$(1,4,2,3,5)=(\begin{array}{ccc}4,2,3,5,1)=(&2,3,5,1,4)=\cdots=(5,1,4,2,3)。\end{array}$

值得注意的是，虽然轮换表达方式比置换更加简洁，轮换不能表达其所在置换的元素数目，需要采用其它方式说明置换的元素数目。  

【例题7.29】将下列置换写成轮换表达的形式。  

$(1)\Big(\begin{matrix}1&2&3&4&5\\1&2&3&4&5\end{matrix}\Big);\quad(2)\Big(\begin{matrix}1&2&3&4&5\\2&3&1&4&5\end{matrix}\Big);\quad(3)\Big(\begin{matrix}1&2&3&4&5\\2&3&4&5&1\end{matrix}\Big)。$

$\textbf{【解】(1)}\begin{pmatrix}1&2&3&4&5\\1&2&3&4&5\end{pmatrix}=(1)=(2)=\cdots=(5);\text{(恒等置换)}$

$(2)\begin{pmatrix}1&2&3&4&5\\2&3&1&4&5\end{pmatrix}=(1 \quad2\quad 3);$

$( 3 ) \begin{pmatrix}1&2&3&4&5\\2&3&4&5&1\end{pmatrix}=(1 \quad2\quad 3\quad 4\quad 5)。$

解毕！  

现在考察轮换的运算。由于轮换是一种特殊的置换，故可像置换那样进行乘法运算。例如，对于集合$ A=\{1,2,3,4,5,6\}$上的两个轮换$(4,1,3,5)$和$(5,6,3)$，则可计算它们的乘积：  

$(4,1,3,5)\cdot(5,6,3)=\begin{pmatrix}1&2&3&4&5&&6\\3&2&5&1&4&&6\end{pmatrix}\cdot\begin{pmatrix}1&2&3&4&5&&6\\1&2&5&4&6&&3\end{pmatrix}$

$=\begin{pmatrix}1&2&3&4&5&&6\\3&2&4&1&6&&5\end{pmatrix}$

$\begin{aligned}(5,6,3)\cdot(4,1,3,5)&=\begin{pmatrix}1&2&3&4&5&6\\1&2&5&4&6&3\end{pmatrix}\cdot\begin{pmatrix}1&2&3&4&5&6\\3&2&5&1&4&6\end{pmatrix}.\\&=\begin{pmatrix}1&2&3&4&5&6\\5&2&6&1&4&3\end{pmatrix}\end{aligned}$

可以看出$(4,\!1,\!3,\!5)\cdot(5,\!6,\!3)\neq(5,\!6,\!3)\cdot(4,\!1,\!3,\!5)$。因此，轮换的乘法不满足交换律。 显然，并不是每个置换都能成为轮换。例如，对于如下8 阶置换：  

$$
\tau=\begin{pmatrix}1&2&3&4&5&6&7\\3&5&6&4&2&1&7\end{pmatrix}
$$

其不可能是轮换。但我们发现：  

$$
\tau=\begin{pmatrix}1&2&3&4&5&6&7\\3&5&6&4&2&1&7\end{pmatrix}
$$

$$
=\bigl(\begin{matrix}1&2&3&4&5&6&7\\3&2&6&4&5&1&7\end{matrix}\bigr)\bigl(\begin{matrix}1&2&3&4&5&6&7\\1&5&3&4&2&6&7\end{matrix}\bigr)
$$

$\quad\quad\quad\quad\quad=(\begin{matrix}1&3&6\\\end{matrix})(\begin{matrix}2&5\\\end{matrix})$

由此可见，$\tau$虽不是轮换，但它可分解成是轮换的乘积。这为解决置换分解问题提供了一个思路。下面考虑对任意置换的轮换分解问题。首先给从下列定义：  

【定义7.15】设$\pi=(i_{1},i_{2},\cdots,i_{t})$和$\tau=(j_{1},j_{2},\cdots,j_{s})$都是轮换，如果$\pi$和$\cdot_{\tau}$不含相同的元素，则称$\pi$与$\tau$是不相交的。  

例如，集合$A=\{1,\!2,\!3,\!4,\!5,\!6\}$上的两个轮换(1,2,5)和(3,4,6)之间是不相交的，而轮换(1,2,5)和(2,4,6)之间则是相交的。  

下面给出对任意置换的轮换分解定理：  

【定理7.10】（轮换分解定理）任一$ n$元置换都可写成若干个不相交轮换的乘积。  

【证明】该定理的证明比较复杂，在此从略。  

上述定理的严格证明过程比较复杂。为使读者加深对该定理的理解，下个结合一个具体例题给出该定理证明的基本思路。  

【例题7.30】将集合$A=\{1,\!2,\!3,\!4,\!5,\!6,\!7,\!8\}$上的下列置换分解成不相交轮换的乘积：  

$$
P=\begin{pmatrix}1&2&3&4&5&6&7&&8\\3&4&6&5&2&1&8&&7\end{pmatrix}
$$

【解】首先，从元素1 开始，发现$P(1)=3$, $P(3)=6$, $P(6)=1$,故得到一个轮换(1,3,6)然后，从$𝐴$不出现在前面轮换中的第一个元素开始，这里是元素2，发现$P(2)=4$, $P(4)=$5, $P(5)=2$,又得到一个轮换(2,4,5)。继续上述过程，此时选元素7，则有$P(7)=8$, $P(8)=$7,得到一个轮换$(7,8)$。故有：$P=(7,8)\cdot(2,4,5)\cdot(1,3,6)$。  

从上述例题的求解过程可以看出，当使用轮换分解定理将置换写成互不相交的轮换之积时，除了乘积的次序可能会有差异之外，分解出的不相交轮换是唯一确定的。不难证明，对于不相交的轮换，它们的乘积满足交换律。因此，置换的轮换分解结果是唯一确定的。  

对于分解为轮换的之积的置换，还可以进一步将其分解为对换的乘积。事实上，对于任意一个轮换$\pi=(i_{1},i_{2},\cdots,i_{k})$,显然有：  

$$
(i_{1},i_{2},\cdots,i_{k})=(i_{1},i_{k})(i_{1},i_{k-1})\cdots(i_{1},i_{3})(i_{1},i_{2})
$$

【例题7.31】将下列置换表示成对换的乘积：  

$$
P=\begin{pmatrix}1&2&3&4&5&6&7&8&9\\3&6&9&5&7&8&4&2&1\end{pmatrix}
$$

【分析】首先该置换转化为若干个不相交轮换的乘积，再将每个轮换分解成对换。  

【解】第一步：依次找出各个轮换。  

$$
\begin{array}{r r r r}{\binom{1}{3}\ \ \ 2}&{3}&{4}&{5}&{6}&{7}&{8}&{9}\\ {\binom{1}{3}\ \ \ 6}&{9}&{5}&{7}&{8}&{4}&{2}&{1}\end{array}\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\!\
$$

第二步：轮换简写格式。  

$$
\begin{pmatrix}1&2&3&4&5&6&7&8&9\\3&6&9&5&7&8&4&2&1\end{pmatrix}=\begin{pmatrix}1&3&9\\3&9&1\end{pmatrix}\begin{pmatrix}2&6&8\\6&8&2\end{pmatrix}\begin{pmatrix}4&5&7\\5&7&4\end{pmatrix};
$$

第三步：轮换分解为对换  

$$
\begin{pmatrix}1&3&9\\3&9&1\end{pmatrix}\begin{pmatrix}2&6&8\\6&8&2\end{pmatrix}\begin{pmatrix}4&5&7\\5&7&4\end{pmatrix}
=(\begin{matrix}{1}&{3}&{9}\\\end{matrix})(\begin{matrix}{2}&{6}&{8}\\\end{matrix})(\begin{matrix}{4}&{5}&{7}\\\end{matrix});
$$

【例题7.32】12 张扑克牌的集合$A=\left\{1,2,3,4,\ \cdots,\ 12\right\}$经过一次洗牌后得到如下对应关系，如表7-6 所示。  

表7-6 一次洗牌对应关系 
![](images/821239d27d0857ad17229da127a64889b83ed6d74f452cc45b1dd0ada81ac160.jpg)  

试问按照同样的洗牌方式，经过几次洗牌可以将牌的顺序恢复到原来的顺序。  

【分析】从已知可以发现，不管怎么洗牌，1 和12 的位置始终不改变，但是其他牌的位置在每次洗牌之后都会发生变化，其变化存在如下规律：  

$$
2{\rightarrow}5{\rightarrow}6{\rightarrow}10{\rightarrow}4{\rightarrow}2,\;\;3{\rightarrow}9{\rightarrow}11{\rightarrow}8{\rightarrow}7{\rightarrow}3
$$

由上面的规律可以知道，经过5 轮的洗牌后，每张牌都将回到原来的位置。所以这是一个5 阶轮换，当轮换置换是$n$ 重轮换时，需要$n$ 次才可以将牌的顺序恢复到原来的顺序。  

【解】按照同样的洗牌方式，经过 5  次洗牌可以将牌的顺序恢复到原来的顺序。  

## $\S7.\,5$ 函数关系的应用  

### 7.5.1 哈希查找问题  

在计算机系统中，数据的存放位置和时间都不能完全确定，此时需要一种有效的方法在有限的存储空间中合理存放数据并且能够实现快速定位查找。此时，如果建立一个关于存储位置和数据关键字的对应关系$f$，就能找给定值$k e y$的像$f(k e y)$。这里的对应关系$f$通常称为哈希函数，这种数据查找方法称为哈希查找。  

例如，如果要建立一张学生成绩表，最简单的方法是以学生的学号作为关键字，1 号学生的记录位置放在第一条，10 号学生的记录位置放在第10 条，以此类推。此时，如果要查看的学号为5 的学生的成绩，则只要取出第5 条记录就可以了.这样建立的表实际上就是一张简单的哈希表，其哈希函数为$f(k e y){=}\ k e y$。然而很多情况下的哈希函数并不如此简单。为了查看的方便，可能会以学生的名字作为关键字。此时，为了能够根据学生的名字直接定位出相应记录所在的位置，需要将这些名字转化为数字，构造出相应的哈希函数，下面给出两个不同的哈希函数：  

（1）考察学生名字的汉语拼音，将其中第一个字母在英语字母表中的序号作为哈希函数值。例如：“蔡军”的汉语拼音第一个字母为字母$C$，因此取03 作为其哈希值。  

（2）考察学生名字的汉语拼音，将其中第一个字母和最后一个字母在英语字母表中的序号之和作为哈希函数值。例如，“蔡军”的汉语拼音第一个字母和最后一个字母分别为$𝐶$和$N$，因此取17 作为其哈希值。  

分别应用这两个哈希函数，成绩表中部分学生名字不同的哈希函数值如表7-7 所示。  

表 7-7 
![](images/a45025876fc98ab470bf113421a83e13ab1997baea6e789cdbd16990f25f7ba0.jpg)  

![](images/0f18f81e6e78fd7fb2b0f104794c8a798e21b0531706abe9d65a4f9970f2f012.jpg)  

在哈希表的构造过程中，可能会出现不同的关键字映射到同一地址的情况，即$k e y_{1}\neq$$k e y_{2}$，但$f(k e y_{1})=f(k e y_{2})$，也将这种现象称为冲突和碰撞。实际上，由于哈希函数是把任意长度的字符串映射为固定长度的字符串，冲突必然存在，只能尽可能减少。常见的构造哈希函数的方法有以下几种：  

（1）数字分析法。数字分析法适合于关键字由若干数码组成，同时各数码的分布规律事先知道的情况。具体方法是：分析关键字集合中每个关键字中的每一位数码的分布情况，找出数码分布均匀的若干位作为关键字的存储地址。例如，一个由80 个结点组成的结构，其关键字为6 位十进制数。选择哈希表长度为100，则可取关键字中的两位十进制数作为结点的存储地址。具体采用哪两位数码，需要用数字分析法对关键字中的数码分布情况进行分析。假设结点中有一部分关键字如下：  

$k e y_{1}=301514\;\;;\;\;\;k e y_{2}=303027;\;\;k e y_{3}=301103;\;\;\;k e y_{4}=308329;$ $k e y_{5}=300287;\;\;k e y_{6}=305939;\;\;k e y_{7}=300792;\;\;k e y_{8}=300463\circ878.$  

对上述关键字分析可以发现，关键字的第一位均是3，第二位均是0，分布集中，不适合作为存储地址。而第4 位和第5 位分布均匀，所以该哈希函数可以构造为取第4,5 位作为结点的存储地址。上述8 个节点的散列地址为：  

$f(k e y_{1})=51~~~~f(k e y_{2})=02~~~~f(k e y_{3})=10~~~~f(k e y_{4})=32$ $f(k e y_{5})=28\;\;\;\;\;f(k e y_{6})=93\;\;\;\;\;f(k e y_{7})=79\;\;\;\;\;f(k e y_{8})=46$  

（2）平方取中法。平方取中法是一种比较常用的构造哈希函数的方法，具体是：将关键字求平方后，取其中间的几位数字作为散列地址。由于关键字平方后的中间几位数字和组成关键字的每一位数字都有关，因此产生冲突的可能性较小，最后究竟取几位数字作为散列地址需要由散列表的长度决定。例如，若结构的存储地址范围是1\~999，则取平方值的中间三位，如表7-8 所示。  

表7-8  平方取中法 
![](images/3bce2eeb41624a2b374dfdbdb4f5d0a22039c970673844c48a904ace588c42b7.jpg)  

（3）除留余数法。除留余数法取关键字被某个不大于哈希表表长$m$的数$ p$除后所得余数为哈希地址，即$f(k e y)=k e y({\bmod{\ p}})$，其中$p\leq m$。这是一种最简单也是最常用的构造哈希函数的方法。它不仅可以对关键字直接取模（mod），也可在平方取中等运算之后取模。值得注意的是，在使用除留余数法时，对$ p$的选择很重要。若$p$选的不好，容易产生同义词。由经验得知：一般情况下可以选$p$为质数或不包含小于20 的质因素的合数。  

哈希函数中会不可避免的存在冲突。因此，在建造哈希函数时不仅要设定一个“好”的哈希函数，而且要设定一种处理冲突的方法。假设哈希表地址集为$\!\sim\!(n-1)$，冲突是指由关键字得到的哈希地址为𝑗$(0\leq j\leq n-1)$的位置上已有记录，则“处理冲突”就是为该关键字的记录找到另一个“空”的哈希地址。  

在处理冲突的过程中可能得到一个地址序列$h_{i}$，其中，$h_{i}\in[0,\mathfrak{n}-1],\mathrm{i}=1,2,\cdots,\mathtt{k}$。即  

在处理哈希地址的冲突时，若得到的另一个哈希地址${\bf h}_{1}$ 仍然发生冲突，则再求下一个地址$h_{2}$，若$ h_{2}$仍然冲突，再求得$h_{3}$，依此类推，直至$h_{k}$不发生冲突为止，则$h_{k}$为记录在表中的地址。处理冲突的具体方法通常有开放定址法、再哈希法和拉链法，这里不再赘述。  

### 7.5.2 宽带分配问题  

随着互联网上语音视频业务的飞速增长，宽带成了影响服务质量的主要因素。一般来说，用户使用的宽带分成两部分：静态宽带和动态宽带。静态宽带是运营商承诺的最小宽带，已经预留给每个用户；动态宽带被所有的用户共享，根据需求进行分配。语音视频业务服务过程一般分成三步：建立连接、进行语音视频传输、结束服务。对于已经建立连接并正在进行传输的服务，运营商应该保证其所需要的宽带。而在连接阶段，如果所有客户申请的宽带总量超过运营商所提供的宽带时，则进行宽带分配。用户的优先级通常他可使用的最大宽带与已占有的宽带之比，需求量越大，被满足的宽带越小，则优先级越高。  

假设已知每一项业务所申请的宽带大小，在保证分配的宽带之和不超过网络总宽带的条件下，如何选择业务，以使得业务优先级收益（即所有业务的优先级之和）达到最大？  

可以用集合与函数对这个问题进行建模。设用户集合是$\{1,2,\cdots,n\}$，用户$𝑖$提出了$t_{i}$个宽带申请，其第$𝑗$个申请的宽带是$r(i,j)$，这里$i=1,\!2,\cdots,n,\:\:\:\mathrm{j}=1,\!2,\cdots,t_{i}.$。假设此刻运营商能提供的动态宽带总量是$B$用户$i$已使用的宽带为$C_{i j}$，可使用的最大宽带为，那么$C_{i j}\leq M_{i j}$。用户$i$的优先级函数记作$P(i,j)$，其中：$P(i,j)=C_{i j}/M_{i j}$。  

用函数$X(i,j)$表示对用户$i$的第𝑗个申请的分配结果$X(i,j)=1$表示分配$X(i,j)=0$表示不分配，那么问题的优化目标是使得下述函数，即优先级利益：  

$$
\sum_{i=1}^{n}\sum_{j=1}^{t_{i}}X(i,j)\cdot P(i,j)\quad\text{(7-9)}
$$

达到最大，同时满足不超过总宽带的约束条件，即：  

$$
\sum_{i=1}^{n}\sum_{j=1}^{t_{i}}X(i,j)\cdot r(i,j)\leq B\quad\text{(7-10)}
$$

这是个典型的组合优化问题，$n$个用户总计有$t_{1}+t_{2}+\cdots+t_{n}=m$个宽带请求，分别标号为${1,2,\cdots,m}$。在考虑前$n$项宽带请求$k=(1,\!2,\cdots,m)$，总宽带限制为$l(l=1,\!2,\cdots,B)$的情况下，设最佳分配的优先级收益为$v(k,l)$。  

如果此时把宽带分配给第$k$项业务（可能是第$𝑖$个用户的第$𝑗$个申请），该业务所需宽带是$r(k)$（在$r(k)=r(i,j)\leq l$的情况下），优先级收益是$P(k)=P(i,j)$。那么，剩下的宽带是$l-$$r(k)$。这些宽带将在${1,2,\cdots,k-1}$项业务中分配，所得到的优先级收益将是$v(k-1,l-r(k))$，因此总的优先级收益是$v(k-1,l-r(k)+P(k))\mathrm{v}$。相反，如果不把宽带分配给第$k$项业务，那么全部宽带𝑙将在${1,2,\cdots,k-1}$项业务中分配，总收益为$v(k-1,l)$为了使得优先级的总收益最大，只要在上述两个收益中选择最大的即可。  

上述分析可以总结成下面的递推公式，即$\forall k(0\leq k\leq m),\forall l(0\leq l\leq B)$，有  

$v(k,l)$  

![](images/ca1bba9e9c93f3e9595cc988da9323614b05bd9b58074b31eaf8aa4a7e6c05f3.jpg)  

根据这个公式：  

第一步先计算$k=1,\mathsf{l}=1,2,\cdots,B$的$v(1,l)$值，并把它们存到一个表中；  

第二步计算$k=2,\mathsf{l}=1,2,\cdots,B$的$v(2,l)$值，再把得到的值存到这个表中。  

每步计算若用到的较小的$v(k,l)$值，就到表中去取。照此做下去，直到计算出$k=m,l=$${1,2,\cdots,B}$的$v(m,l)$值为止，其中的$v(m,B)$就是最佳分配的优化函数值，即最大优先级收益。  

上述计算完成后，再根据$v(m,B)$的值逐步向前追溯，就可以找到最佳分配方案。先看$v(m,B)$是等于$v(m-1,B)$，还是等于$v\bigl(m-1,B-r(m)\bigr)+P(m)\,?$若等于前者，则没有选择第$m$项业务；若等于后者，则选择了第$m$项业务。然后根据剩下的部分是$v(m-1,B)$还是$v\big(m-1,B-r(m)\big)$来追溯第$m-1$项业务是否被选到。照此下去，直到$m$项业务都考察到，就得到问题的解。如果在计算每一项$v(k,l)$的时刻就把是否选择第$k$项业务记录下来，则就可以省略追溯过程，只需查一下全部记录，就能得到了问题的解。  

## $\S7.\,6$ 习 题 <abc>

1.对于集合$A=\{x,y,z\}$，$B=\{1,\!2,\!3\}$,判断下面𝐴到$B$的哪些关系构成函数.  

$\{\langle x,1\rangle,\langle x,2\rangle,\langle\mathbf{y},\mathbf{1}\rangle,\langle\mathbf{y},\mathbf{3}\rangle\};\;\;\mathrm{(2)}\;\;\{\langle x,1\rangle,\langle\mathbf{y},3\rangle,\langle z,3\rangle\};\;\;\mathrm{(3)}\;\;\{\langle x,1\rangle,\langle\mathbf{y},1\rangle,\langle z,1\rangle\};$ $\{\langle x,2\rangle,\langle y,3\rangle\};\;\;(\mathrm{\boldmath~5~})\;\;\{\langle x,1\rangle,\langle y,2\rangle,\langle z,3\rangle\};\;\;(\mathrm{\boldmath~6~})\;\;\{\langle x,1\rangle,\langle x,2\rangle,\langle y,1\rangle,\langle y,3\rangle,\langle z,2\rangle,\langle z,3\rangle\}.

$ 2. 在下面哪些关系中哪些能构成函数？ 

$\{\langle x_{1},x_{2}\rangle|x_{1},x_{2}\in N,x_{1},x_{2}<10\};\,\{\langle x_{1},x_{2}\rangle|x_{1},x_{2}\in R,x_{1}={x_{2}}^{2}\};\,\{\langle x_{1},x_{2}\rangle|x_{1},x_{2}\in R,{x_{1}}^{2}=x_{2}\}\,.

$ 3. 设$f,g$都是$A\rightarrow A$的函数，证明$f\cap g$是函数。 

4. 假设$f$和$g$是函数，证明$f\subseteq g\Leftrightarrow\,\mathrm{dom}\ f\subseteq\mathrm{dom}\ g,$，且对$\forall x\in d\mathrm{om}\,\,f$，有$f(x)=g(x)$。 

5. 设$R,Z,N$分别表示实数、整数和自然数集，定义如下函数$f_{1},f_{2},f_{3},f_{4}$，试讨论其是单射、满射还是双射：  

$f_{1}\colon R\rightarrow R^{+},f_{1}(x)=2^{x};\;\;(\,2\,)\;\;f_{2}\colon\mathrm{Z}\rightarrow\mathrm{N},f_{2}(x)=|x|;$ （ 3 ） $f_{3}\colon N\to N,f_{3}(x)=2x\,$ ； （ 4 ） $f_{4}$ : 𝑁→𝑁× 𝑁, 𝑓 4 (𝑥) = 〈𝑥, 𝑥+ 1〉 .  

6.  设 $|\mathrm{A}|=n$ ,   $|\mathrm{B}|=m$  

(1) 从A到B有多少个不同的函数； (2) 当$n$，$m$满足什么条件时,存在双射,且有多少不同的双射？(3) 当$n$，$m$满足什么条件时,存在满射,且有多少不同的满射? (4) 当$n$，$m$满足什么条件时,存在单射,且有多少不同的单射?  

7. 设函数𝑓:$N\rightarrow N$，且有：  

$f(1)=1,\ f(n+1)={\left\{\begin{array}{l l}{f(n)/2\,,}\\ {5f(n)+1}\end{array}\right.}$  

说明$f(x)$既不是满射，又不是单射。  

8. 试给出满足下列每个条件的函数例子：  

（1）是单射而不是满射；   （2）是满射而不是单射；（3）不是单射也不是满射； （4）既是单射也是满射。  

9.设$f\colon R\to R$，$R$ 为实数集，对下面各个$^ Ḋ f Ḍ$判断它是否为单射、满射或双射。如果不是单射，则给出$x_{1}$和$x_{2}$,使得$x_{1}\neq x_{2}$且$f(x_{1})=f(x_{2})$；如果不是满射，则计算$f(R)$。  

(1) $f(x)=x^{2}$；(2) $\begin{array}{r}{f(x)=E[x],}\end{array}$,其中$E[x]$表示小于等于$\mathbf{X}$ 的最大整数。  

10. 设$A=\{a,b,c\},R=\{\langle a,b\rangle,\langle b,a\rangle\}\cup I_{A}$是𝐴上的等价关系，设自然映射$\cdot g\!:A\to A/R$，求$.g(a)

$11. 设$f\colon A\to A$，$B$是𝐴的子集，试确定$f(f^{-1}(B))$、$B$和$f^{-1}(f(B))$三者之间包含关系。 

12.设$f,g,h$都是实数集$R$上的函数,对$\forall x\in R,f(x)=2x+1,g(x)=5+x,h(x)=x/2$。求：  

$$
f\circ g,\ \ \mathbf{g}\circ f,\ \ \mathrm{h}\circ f,\ \ \ f\circ(h\circ g),\!\mathbf{g}\circ(\mathrm{h}\circ f)
$$

13. 两个从自然数集$N$到$|N$的位移函数为$f(n)=n+1$， $g(n)=\operatorname*{max}\{0,n-1\}$。证明：  

（1）$f$是单射而不是满射；（2）$g$是满射而不是单射；（3）$f\circ g=I_{N}$, 但$g\circ f\ne I_{N}$。

14. 设$\cdot f,g\in N^{N},N$为自然数集，且有：  

$$
f(x)=\left\{\begin{array}{c c}{{x+1,x=0,1,2,3}}\\ {{0,}}\\ {{x,}}\end{array}\right.\quad\quad\quad\quad x=4;\;\;g(x)=\left\{\begin{array}{c c}{{x/2\,,x\,\overbar{\mu}\,\overbar{\mu}\,\frac{3\mu}{2\bar{\chi}}}}\\ {{3,x\,\overbar{\mu}\,\overbar{\mu}\,\frac{3\mu}{2\bar{\chi}}\,\frac{3\mu}{2\bar{\chi}}}}\end{array}\right.
$$

（1）求$f\circ g$，并讨论它的性质（是否为单射或满射）. 

   （2）设$A=\{0,1,2\}$，$B=\{0,1,5,6\}$，求𝐴在$f\circ g$下的像$f\circ g(A)$和$B$的完全原像$f\circ g^{-1}(B)$.  

15. 令$\cdot f$是从𝐴到$B$的函数，令𝑆和𝑇为𝐴的子集，求证： $f(S\cup T)=f(S)\cup f(T);\ \ (\,2\,)\ \,f(S\cap T)\subseteq\ \,f(S)\cap f(T)$ $f^{-1}(S\cup T)=f^{-1}(S)\cup f^{-1}(T);\ \ (4)\ \,f^{-1}(S\cap T)=f^{-1}(S)\cap f^{-1}(T)

$ 16. 令𝑆为全集$U$的子集，$S$的特征函数$f_{S}$是从$U$到集合{0,1}的函数：若$x\in S$，则$f_{S}(x)=1$；若$x$不属于𝑆，则$f_{S}(x)=0$。令$^{A,B}$为集合，求证： $f_{A\cap B}(x)=f_{A}(x)\cdot f_{B}(x);\;\;(\;2\;)\;\;f_{A\cup B}(x)=f_{A}(x)+f_{B}(x)-f_{A}(x)\cdot f_{B}(x)$ $f_{\bar{A}}(x)=1-f_{A}(x);\;\;(4)\;\;f_{A\oplus B}(x)=f_{A}(x)+f_{B}(x)-2f_{A}(x)f_{B}(x)

$ 17. 设$f\colon S\to T$，证明： 

（1）$f(A\cap B)\subseteq f(A)\cap f(B)$，其中$A,B$是𝑆的子集。 

（2）举出反例说明等式$f(A\cap B)=f(A)\cap f(B)$不是永远为真的。 

（3）说明对于什么函数，上述等式为真。 

18. 设$A=\{1,\!2,\!3,\!4\}$，$A_{1}=\{1,2\},A_{2}=\{1\},A_{3}=\emptyset$，求$.A_{1}$，$A_{2}$，$A_{3}$和𝐴的特征函数。 

19.对于集合$A=\{a,b,c,d\}$，$B=\{1,\!2,\!3\}$，$C=\{a,b,d\}$，计算如下函数的复合函数： $f=\{\langle a,1\rangle,\langle b,2\rangle,\langle c,1\rangle,\langle d,3\rangle\},\,\,\,g=\{\langle1,a\rangle,\langle2,b\rangle,\langle3,d\rangle\};$ $f=\{\langle a,2\rangle,\langle b,3\rangle,\langle c,1\rangle,\langle d,3\rangle\},\,\,\,g=\{\langle1,a\rangle,\langle2,a\rangle,\langle3,a\rangle\};$ $f=\{\langle a,3\rangle,\langle b,1\rangle,\langle c,2\rangle,\langle d,3\rangle\},\,\,\,g=\{\langle1,b\rangle,\langle2,b\rangle,\langle3,b\rangle\};$ $f=\{\langle a,2\rangle,\langle b,2\rangle,\langle c,3\rangle,\langle d,3\rangle\},\;\;g=\{\langle1,d\rangle,\langle2,b\rangle,\langle3,a\rangle\}\,\mathrm{.}

$ 20. 令$f(x)=a x+b$和$g(x)=c x+d$，其中$a,b,c,d$为常数。确定常数使得：$f\circ g{=}g\circ f$。 

21. 使用集合特征函数证明下面集合恒等式：  

$$
(1)A\cap(B\cup\sim A)=B\cap A;\ \ (2)A\cap(B\cup C)=(A\cap B)\cup(A\cap C)\circ
$$

22. 设𝑆为集合，$A,B$是$S$的子集，$\chi_{T}$表示 $T$的特征函数，且$\chi_{A}=\{\langle a,1\rangle,\langle b,1\rangle,\langle c,0\rangle,\langle d,0\rangle\},

$ ${{\chi}_{B}}=\{\langle a,0\rangle,\langle b,1\rangle,\langle c,0\rangle,\langle d,1\rangle\}$，求$\chi_{A\cap B}$。  

23.  设置换 $\begin{array}{l l l l l l}{\cdot s=\binom{1}{2}}&{2}&{3}&{}&{4}&{5}\\ {\cdot2}&{4}&{3}&{}&{5}&{1}\end{array},\;\;t=\binom{1}{2}\begin{array}{l l l l l l}{1}&{2}&{3}&{}&{4}&{5}\\ {2}&{5}&{1}&{}&{4}&{3}\end{array},$ ，求 𝑠 2 , 𝑡 2 , 𝑠𝑡 ,  𝑡𝑠 ,   $s^{-1}$ ,   $t^{-1}$ $\mathfrak{i}s=\binom{a}{g}\;\;\;b\;\;\;c\;\;\;d\;\;\;e\;\;\;f\;\;\;g\atop f\quad e\;\;\;d\;\;\;c\;\;\;b\;\;\;s\bigg),\;\;t=\binom{a\quad b\quad c\quad d\quad e\;\;\;f\quad g\atop e\quad g\quad f\quad b\quad a\quad c\quad d\bigg),

$  

(1) 求出上述置换的逆置换； (2) 计算 $.s\circ t(a),t\circ s(a),s^{-1}(b)\circ t^{-1}(c)$ ； (3) 计算 $s\circ t,t\circ s$ 。  