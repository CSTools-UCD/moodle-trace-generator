# Moodle Trace Generator
Moodle trace generator is a command line utility for generating code tracing exercises which can be imported as moodle cloze questions. Questions can be focused on a single simple statement, or at a higher level on a number of statements.

## High Level Questions
Generating questions at a high level about overall execution of the code and changes to the variables is the default behaviour. This can be achieved with the following command.
```
python3 main.py example.py
```

If the contents of the file `example.py` are the following, then the question below will be generated. 
```python
a = 10
b = a * 23 + 12
```

### The Generated Question
![Example of high level question](doc/01.high.example.png)

This type of question is suitable for use reinforcing students knowledge of the flow of control in programs. Default behaviour is to award points for correct variable values (at the point of change), correct sequence of line execution, evaluation of expressions and determination of type. Many of these are choosen from options in a drop-down menu, while calculation result and values of variables must be typed by the students.

### The Generated Feedback
For the default settings, the following flowchart is displayed after the question is submitted. It is a very basic generated representation of the steps that the program executes in order.
![Flowchart showing execution of the lines of code](doc/01.high.feedback.svg)


### Animated Feedback
By adding the command line flag `-a` the above feedback is replaced with an animated representation of the same, with a represenation of the code and a redementary symbol table.

![Animated flowchart showing execution of the lines of code](doc/01.high.animated.feedback.svg)


## Low Level Questions
To generate low-level questions we can add the command line flag `-i`. This causes the generation of individual questions for each line of code. These questions focus on the execution order of expressions within the statement. 

```
python3 main.py example.py -i
```
### The Generated Question
This question is generated based on the second line of code in the example.py above.

![Example of low level question](doc/02.low.example.png)

All inputs except the result and value columns are choosen from drop-down boxes, while these must be typed by the student. 

### The Generated Feedback
For the default settings, the following image is displayed after the question is submitted. It is a very basic generated representation of the AST for that line of code. This image is accompanied with a block of text explaining the ordering of the operations. 

![Flowchart showing execution of the lines of code](doc/02.low.feedback.svg)


### Animated Feedback
By adding the command line flag `-a` the above feedback is replaced with an animated representation of the same. Little is changed, but nodes in the tree are highlighted in sequence and results are animated travelling up the tree in sequence. 

![Animated flowchart showing execution of the lines of code](doc/02.low.animated.feedback.svg)