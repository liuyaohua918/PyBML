# Welcome to the documentation for BOML

## Contents <div0 id="a0"></div0>
1. [Introduction ](#a1)<br>
2. [Installation and Requirements ](#a2)
3. [Quickly Build Your Bilevel Meta-Learning Model ](#a3)
    - [Core Modules ](#a31)
    - [Core Built-in Functions of BOMLOptimizer ](#a32)
    - [Simple Training Example](#a33)
4. [Modification and Extension ](#a4)
5. [Authors and Liscense](#a5)

## Introduction <div1 id="a1"></div1>
BOML is a bilevel optimization library in Python for meta learning. Before reading the documentation, you could refer to [View on GitHub](https://github.com/dut-media-lab/BOML) for a brief introduction about meta learning and BOML. <br>
Here we provide detailed instruction to quickly get down to your research and test performance of popular algorithms and new ideas.

## Installation and requirements  <div2 id="a2"></div2>
BOML implements various meta learning approaches based on [TensorFlow](https://www.tensorflow.org/install/pip), which is one of the most popular macheine learning platform. Besides, [Numpy](https://numpy.org/install/) and basical image processing modules are required for installation. <br>
We also provide [requirements.txt](https://github.com/dut-media-lab/BOML/blob/master/requirements.txt) as reference for version control.
BOML requires Python 3.5+ and TensorFlow 1.13+.

  ```
  1. Install from GitHub page：

  git clone https://github.com/liuyaohua918/boml.git

  python setup.py install 
  
  or
  
  pip install -r requirements.txt

  2. use pip instruction

  pip install boml
  
  or
  
  pip install --upgrade boml
  ```
 
## Quickly build your bilevel meta-learning model <div3 id="a3"></div3>
  - Core Modules: <div3 id="a31"></div3>
    1. load_data
       - Related: 
            - boml.load_data.meta_omniglot <br>
            - boml.load_data.meta_mini_imagenet <br>
            - boml.load_data.mnist <br>
            - ...
        ```
        boml.meta_omniglot(
            folder=DATA_FOLDER, 
            std_num_classes=None, 
            examples_train=None, 
            examples_test=None, 
            one_hot_enc=True, 
            _rand=0, 
            n_splits=None)
        boml.meta_mini_imagenet(
          folder=DATA_FOLDER, 
          sub_folders=None, 
          std_num_classes=None,
          examples_train=None, 
          examples_test=None, 
          resize=84, 
          one_hot_enc=True, 
          load_all_images=True,
          h5=False):
        ```
        boml.load_data manages different datasets and generate batches of tasks for training and testing.

       - Args：<br>
            - folder: str, root folder name. Use os module to modify the path to the datasets. For example, os.environ["DATASETS_FOLDER"] = "../data/"<br>
            - std_num_classes: int, number of classes for N-way classification<br>
            - examples_train: int, number of examples to be picked in each generated per classes for training (eg .1 shot, examples_train=1)<br>
            - examples_test: int, number of examples to be picked in each generated per classes for testing
            - one_hot_enc: BOOLEAN, whether to adopt one hot encoding<br>
            - _rand: int, random seed or RandomState for generate training, validation, testing meta-datasets split<br>
            - n_splits: num of classes per split<br>
       - Usage:
          ```
          dataset = boml.meta_omniglot(args.num_classes,
                                  (args.num_examples, args.examples_test))
          ```
       - Returns: an initialized instance of data loader 
    2. BOMLExperiment
       - Aliases: 
           - boml.load_data.BOMLExperiment
        ```
        boml.BOMLExperiment(
            dataset=None, 
            dtype=tf.float32)
        ```
        boml.BOMLExperiment manages inputs, outputs and task-specific parameters.
       - Args:
          - dataset: initialized instance of load_data<br>
          - dtype: default to be float32<br>
       - Attributes:<br>
          - x: input placeholder of input for your defined lower level problem<br>
          - y: label placeholder of output for yourdefined lower level problem<br>
          - x_:input placeholder of input for your defined upper level problem<br>
          - y_:label placeholder of output for your defined upper level problem<br>
          - model: used to restore the task-specific model <br>
          - errors: dictionary to restore defined loss functions of different levels<br> 
          - scores: dictionary to restore defined accuracies functions<br> 
          - optimizer: dictonary to restore optimized chosen for inner and outer loop optimization<br>
       - Usage:
        ```
        ex = boml.BOMLExperiment(datasets = dataset)
        ex.errors['training'] = boml.utils.cross_entropy(pred=ex.model.out, label=ex.y, method='MetaRper')
        ex.scores['accuracy'] = tf.contrib.metrics.accuracy(tf.argmax(tf.nn.softmax(ex.model.out), 1), tf.argmax(ex.y, 1))
        ex.optimizer['apply_updates'], _ = boml.BOMLOptSGD(learning_rate=lr0).minimize(ex.errors['training'],var_list=ex.model.var_list)
        ```
       - Returns: an initialized instance of BOMLExperiment 
  
    3. BOMLOptimizer 
       - Aliases: 
         - boml.boml_optimizer.BOMLOptimizer
        ```
        boml.BOMLOptimizer(
            Method=None, 
            inner_method=None, 
            outer_method=None, 
            truncate_iter=-1,
            experiments=[]
            )
        ```
        BOMLOptimizer is the main class in `boml`, which takes responsibility for the whole process of model construnction and back propagation. 
       - Args:
          - Method: str, define basic method for following training process, it should be included in [`MetaInit`, `MetaFeat`], `MetaInit` type includes methods like `MAML`, `FOMAML`, `MT-net`, `WarpGrad`; `MetaFeat` type includes methods like `BDA`, `RHG`, `TRHG`, `HOAG`, `DARTS`;<br>
          - inner_method: method chosen for solving LLproblem, including [`Trad` ,`Simple`, `Aggr`], MetaInit type choose either `Trad` for traditional optimization strategies or `Aggr` for Gradient Aggragation optimization. 'MetaInit' type should choose `Simple`, and set specific parameters for detailed method choices like FOMAML or MT-net.<br>
          - outer_method: str, method chosen for solving LLproblem, including [`Reverse` ,`Simple`, `DARTS`, `Implcit`], `MetaFeat` type should choose `Simple`, and set specific parameters for detailed method choices like `FMAML`
          - truncate_iter: str, specific parameter for `Truncated Gradient(TRHG)` method, defining number of iterations to truncate in the Back propagation process<br>
          - experiments: list of BOMLExperiment objects that has already been initialized <br>
        - Usage:
        ```
        ex = boml.BOMLExperiment(boml.meta_omniglot(5,1,15))
        boml_ho = boml.BOMLOptimizer(
            Method='MetaInit', 
            inner_method='Simple', 
            outer_method='Simple',
            experiments=ex)
        ```
       - Utility Functions:
          - learning_rate(): returns defined inner learning rate
          - meta_learning_rate(): returns defined outer learning rate 
          - Method: return defined method type 
          - param_dict: return the dictionary that restores general parameters, like use_t,use_warp, output shape of defined model, learn_lr, s, t, alpha, first_order.
       - Returns: an initialized instance of BOMLOptimizer
	   
  - Core Built-in functions of BOMLOptimizer: <div3 id="a32"></div3> 
    1. BOMLOptimizer.meta_learner:
       - Aliases: 
         - boml.boml_optimizer.BOMLOptimizer.meta_learner()
        ```
        boml.boml_optimizer.BOMLOptimizer.meta_learner(
            _input, 
            dataset, 
            meta_model='V1', 
            name='Hyper_Net', 
            use_t=False, 
            use_warp=False,
            **model_args
        )
        ```
       This method must be called once at first to build meta modules and initialize meta parameters and neural networks.
       - Args:
          - _input: orginal input for neural network construction;
          - dataset: which dataset to use for training and testing. It should be initialized before being passed into the function
          - meta_model: model chosen for neural network construction, `V1` for C4L with fully connected layer,`V2` for Residual blocks with fully connected layer.
          - name: name for Meta model modules used for BOMLNet initialization
          - use_t: whether to use T layer for C4L neural networks
          - use_warp: whether to use Warp layer for C4L neural networks
          - model_args: optional arguments to set specific parameters of neural networks.
  
    2. BOMLOptimizer.base_learner:
       - Aliases: 
          - boml.boml_optimizer.BOMLOptimizer.base_learner()
        ```
        boml.boml_optimizer.BOMLOptimizer.base_learner(
            _input, 
            meta_learner, name='Task_Net',
            weights_initializer=tf.zeros_initializer
        )
        ```
       This method has to be called for every experiment and takes responsibility for defining task-specific modules and inner optimizer.
       - Args:
          - _input: orginal input for neural network construction of task-specific module;
          - meta_learner: returned value of meta_learner function, which is a instance of BOMLNet or its child classes
          - name: name for Base model modules used for BOMLNet initialization
          - weights_initializer: initializer function for task_specific network, called by 'MetaInit' method
       - Returns: task-specific model part

    3. BOMLOptimizer.ll_problem:
       - Aliases: 
             - boml.boml_optimizer.BOMLOptimizer.ll_problem()
        ```
        boml.boml_optimizer.BOMLOptimizer.ll_problem(
              inner_objective,
              learning_rate, 
              T, 
              inner_objective_optimizer='SGD', 
              outer_objective=None,
              learn_lr=False, 
              alpha_init=0.0, 
              s=1.0, t=1.0, 
              learn_alpha=False, 
              learn_st=False,
              learn_alpha_itr=False, 
              var_list=None,
              init_dynamics_dict=None, 
              first_order=False, 
              loss_func=utils.cross_entropy, 
              momentum=0.5,
              beta1=0.0,
              beta2=0.999,
              regularization=None, 
              experiment=None, 
              scalor=0.0, 
              **inner_kargs
        )
        ```
       After construction of neural networks, solutions to lower level problems should be regulated in ll_problem.
       - Args:
          - inner_objective: loss function for the inner optimization problem
          - learning_rate: step size for inner loop optimization
          - T: numbers of steps for inner gradient descent optimization
          - inner_objective_optimizer: Optimizer type for the outer parameters, should be in list [`SGD`,`Momentum`,`Adam`]
          - outer_objective: loss function for the outer optimization problem, which need to be claimed in BDA agorithm
          - alpha_init: initial value of ratio of inner objective to outer objective in BDA algorithm
          - s,t: coefficients of aggregation of inner and outer objectives in BDA algorithm, default to be 1.0
          - learn_alpha: specify parameter for BDA algorithm to decide whether to initialize alpha as a hyper parameter
          - learn_alpha_itr: parameter for BDA algorithm to specify whether to initialize alpha as a vector, of which every dimension's value is step-wise scale factor fot the optimization process        
          - learn_st: specify parameter for BDA algorithm to decide whether to initialize s and t as hyper parameters
          - first_order: specific parameter to define whether to use implement first order MAML, default to be `FALSE`
          - loss_func: specifying which type of loss function is used for the maml-based method, which should be consistent with the form to compute the inner objective
          - momentum: specific parameter for Optimizer.BOMLOptMomentum to set initial value of momentum
          - regularization: whether to add regularization terms in the inner objective 
          - experiment: instance of BOMLExperiment to use in the Lower Level Problem, especifially needed in the `MetaFeat` type of method.
          - var_list: optional list of variables (of the inner optimization problem)
          - inner_kargs: optional arguments to pass to `boml.boml_optimizer.BOMLOptimizer.compute_gradients`
       - Returns: task-specific model part
   
    4. BOMLOptimizer.ul_problem
       - Aliases:
          - boml.boml_optimizer.BOMLOptimizer.ul_problem()
            ```
            boml.boml_optimizer.BOMLOptimizer.ul_Problem(
                outer_objective, 
                meta_learning_rate, 
                inner_grad,
                meta_param=None, 
                outer_objective_optimizer='Adam', 
                epsilon=1.0,
                momentum=0.5, 
                global_step=None
            )
            ```
        This method define upper level problems and choose optimizer to optimize meta parameters, which should be called afer ll_problem.
        - Args:
            - outer_objective: scalar tensor for the outer objective
            - meta_learning_rate: step size for outer loop optimization
            - inner_grad: Returned value of boml.BOMLOptimizer.LLProblem()
            - meta_param: optional list of outer parameters and model parameters
            - outer_objective_optimizer: Optimizer type for the outer parameters, should be in list [`SGD`,`Momentum`,`Adam`]
            - epsilon: Float, cofffecients to be used in DARTS algorithm
            - momentum: specific parameters to be used to initialize `Momentum` algorithm
        - Returns：meta_param list, used for debugging
    5. aggregate_all:
       - Aliases: 
           - boml.boml_optimizer.BOMLOptimizer.aggregate_all()
          ```
          boml.boml_optimizer.BOMLOptimizer.aggregate_all(
              aggregation_fn=None, 
              gradient_clip=None
              )

          ```
       - Args:
          - aggregation_fn:Optional operation to aggregate multiple outer_gradients (for the same meta parameter),by (default: reduce_mean)
          - gradient_clip: optional operation to clip the aggregated outer gradients
       - Returns: None
     Finally, aggregate_all has to be called to aggregate gradient of different tasks, and define operations to apply outer gradients and update meta parametes.
    6. run:
       - Aliases: 
          - boml.boml_optimizer.BOMLOptimizer.run()
        ```
        boml.boml_optimizer.BOMLOptimizer.run(
            inner_objective_feed_dicts=None,
            outer_objective_feed_dicts=None,
            session=None, 
            _skip_hyper_ts=False, 
            _only_hyper_ts=False, 
            callback=None
        )
        ```
       - Args:
          - inner_objective_feed_dicts: an optional feed dictionary for the inner problem. Can be a function of step, which accounts for, e.g. stochastic gradient descent.
          - outer_objective_feed_dicts: an optional feed dictionary for the outer optimization problem (passed to the evaluation of outer objective). Can be a function of hyper-iterations steps (i.e. global variable), which may account for, e.g. stochastic evaluation of outer objective.
          - session: optional session
          - callback: optional callback function of signature (step (int), feed_dictionary, `tf.Session`) -> None that are called after every forward iteration.
       - Returns: None
  
  - Simple Running Example <div3 id="a33"></div3>
    #### Start from loading data
      ```python
      import boml
      from boml import utils
      from test_script.script_helper import *

      dataset = boml.load_data.meta_omniglot(
          std_num_classes=args.classes,
          examples_train=args.examples_train,
          examples_test=args.examples_test,
      )
      # create instance of BOMLExperiment for ong single task
      ex = boml.BOMLExperiment(dataset)

      ```

    #### Build network structure and define parameters for meta-learner and base-learner
    ```python
    boml_ho = boml.BOMLOptimizer(
        method="MetaInit", inner_method="Simple", outer_method="Simple"
    )
    meta_learner = boml_ho.meta_learner(_input=ex.x, dataset=dataset, meta_model="V1")
    ex.model = boml_ho.base_learner(_input=ex.x, meta_learner=meta_learner)
    ``` 
    #### Define LL objectives and LL calculation process
    ```python
    loss_inner = utils.cross_entropy(pred=ex.model.out, label=ex.y)
    accuracy = utils.classification_acc(pred=ex.model.out, label=ex.y)
    inner_grad = boml_ho.ll_problem(
        inner_objective=loss_inner,
        learning_rate=args.lr,
        T=args.T,
        experiment=ex,
        var_list=ex.model.var_list,
    )
    ```
    #### Define UL objectives and UL calculation process
    ```python
    loss_outer = utils.cross_entropy(pred=ex.model.re_forward(ex.x_).out, label=ex.y_)
    boml_ho.ul_problem(
        outer_objective=loss_outer,
        meta_learning_rate=args.meta_lr,
        inner_grad=inner_grad,
        meta_param=tf.get_collection(boml.extension.GraphKeys.METAPARAMETERS),
    )
    ```
    #### Aggregate all the defined operations
    ```python
    # Only need to be called once after all the tasks are ready
    boml_ho.aggregate_all()
    ```
    #### Meta training iteration
    ```python
    with tf.Session() as sess:
        tf.global_variables_initializer().run(session=sess)
        for itr in range(args.meta_train_iterations):
            # Generate the feed_dict for calling run() everytime
            train_batch = BatchQueueMock(
                dataset.train, 1, args.meta_batch_size, utils.get_rand_state(1)
            )
            tr_fd, v_fd = utils.feed_dict(train_batch.get_single_batch(), ex)
            # Meta training step
            boml_ho.run(tr_fd, v_fd)
            if itr % 100 == 0:
                print(sess.run(loss_inner, utils.merge_dicts(tr_fd, v_fd)))
    ```
    
## Modification and extension  <div4 id="a4"></div4>
  - Extensible Base Calsses and Modules
    1. BOMLNet 
       - Aliases：
          - boml.networks.BOMLNet
       - Methods to be overridden:
            - forward()：
                uses defined convolutional neural networks with initial input
            - re_forward(new_input): 
                reuses defined convolutional with new input and update the output results 
            - create_outer_parameters(): 
              this method creates parameters of upper level problems, and adds them to defined collections named `METAPARAMETERS`
                - Args: 
                  - var_collections: collections to restore meta parameters created in the so called scope 
                - Returns: dictionary that indexes the outer parameters 
            - create_model_parameters(): 
                this method creates model parameters of upper level problems like `t-layer` or `Warp-layer` , and adds them to define collections called `METAPARAMETERS`
       - Utility functions:
            - get_conv_weight(boml_net, layer, initializer):
                - Args:
                  - boml_net: initialized instance of BOMLNet
                  - layer: int32, the layer-th weight of convolutional block to be created
                  - initializer: the tensorflow initializer used to initialize the filters 
              -Returns: created parameter
            - get_bias_weight(boml_net, layer, initializer):
                - Args:
                  - boml_net: initialized instance of BOMLNet
                  - layer: int32, the layer-th bias of convolutional block to be created
                  - initializer: the tensorflow initializer used to initialize the bias
                - Returns: created parameter
            - get_identity(dim, name, conv=True):
                - Args:
                  - dim: the dimension of identity metrix
                  - name: name to initialize the metrix
                  - conv: BOOLEAN , whether initialize the metrix or initialize the real value, default to be True
                - Returns: the created parameter
            - conv_block(boml_net, cweight, bweight):
               uses defined convolutional weight and bias with current ouput of boml_net
                - Args:
                  - boml_net: initialized instance of BOMLNet
                  - cweight: parameter of convolutional filter
                  - bweight: parameter of bias for convolutional neural networks
            - conb_block_t(boml_net, conv_weight, conv_bias, zweight):
               uses defined convolutional weight, bias, and weights of t layer  with current ouput of boml_net
                - Args:
                  - boml_net: initialized instance of BOMLNet
                  - cweight: parameter of convolutional filter
                  - bweight: parameter of bias for convolutional neural networks
            - conv_block_warp(boml_net, cweight, bweight, zweight, zbias):
              uses defined convolutional weight, bias and filters of warp layer  with current ouput of boml_net
                - Args:
                  - boml_net: initialized instance of BOMLNet
                  - cweight: parameter of convolutional filter
                  - bweight: parameter of bias for convolutional neural networks
    2. BOMLInnerGrad
       - Aliases:
          - boml.LLProblem.BOMLInnerGrad
       - Methods to be overridden:
           - compute_gradients(boml_opt, loss_inner, loss_outer=None,inner_method=None, param_dict=OrderedDict(), var_list=None, **inner_kargs):
        delivers equivalent functionality to the method called compute_gradients() in `tf.train.Optimizer`
            - Args:
              - boml_opt: instance of boml.optimizer.BOMLOpt, which is automatically create by the method in `boml.boml_optimizer.BOMLOptimizer` 
              - loss_inner: inner objective, which could be passed by `boml.boml_optimizer.BOMLOptimizer.ll_problem` or called directly.
              - loss_outer: outer objective,which could be passed automatically by `boml.boml_optimizer.BOMLOptimizer.ll_problem`, or called directly 
              - param_dict: automatically passed by 'boml.boml_optimizer.BOMLOptimizer.ll_problem'
              - var_list: list of lower level variables
              - inner_kargs: optional arguments, which are same as `tf.train.Optimizer`
            - Returns：self   
       - Utility functions:
          - apply_updates():
            Descent step, as returned by `tf.train.Optimizer.apply_gradients`.
          - initialization():
            a list of operations that return the values of the state variables for this learning dynamics after the execution of the initialization operation. If an initial dynamics is set, then it also executed.
          - state(): 
            A generator for all the state variables (optimized variables and possibly auxiliary variables) being optimized
    3. BOMLOuterGrad
       - Aliases: 
         - boml.ul_problem.BOMLOuterGrad
       - Methods to be overridden:
         - compute_gradients(outer_objective, bml_inner_grad, meta_param=None):
            - Args:
              - bml_inner_grad: OptimzerDict object resulting from the inner objective optimization.
              - outer_objective: A loss function for the outer parameters (scalar tensor)
              - meta_param: Optional list of outer parameters to consider. If not provided will get all variables in the hyperparameter collection in the current scope.
            - Returns: list of meta parameters involved in the computation
          - apply_gradients( inner_objective_feed_dicts=None, outer_objective_feed_dicts=None, initializer_feed_dict=None, param_dict=OrderedDict(), train_batches=None, experiments= [], global_step=None, session=None, online=False, callback=None)
            - Args:
              - inner_objective_feed_dicts: Optional feed dictionary for the inner objective
              - outer_objective_feed_dicts: Optional feed dictionary for the outer objective
                                              (note that this is not used in ForwardHG since hypergradients are not
                                              variables)
              - initializer_feed_dict: Optional feed dictionary for the inner objective
              - global_step: Optional global step for the optimization process
              - param_dict: dictionary of parameters passed by `boml.boml_optimizer.BOMLOptimizer`
              - train_batches: mini batches of data, needed when Reptile Algorithm are implemented
              - session: Optional session (otherwise will take the default session)
              - experiments: list of instances of `BOMLExperiment`, needed when Reptile Algorithm are implemented
              - callback: callback funciton for the forward optimization
       - Utility functions:
         - outer_grads_and_vars(meta_param=None, aggregation_fn=None, gradient_clip=None):
                Method for getting outergradient and outer parameters as required by apply_gradient methods from tensorflow optimizer.
                - Args：
                  - meta_param: Optional list of outer parameters to consider. If not provided will get all variables in the hyperparameter collection in the current scope.
                  - aggregation_fn: Optional operation to aggregate multiple outer gradients (for the same parameter of meta-learner), by default reduce_mean
                  - gradient_clip: Optional operation like clipping to be applied.
         - initialization():
                 Returns groups of operation that initializes the variables in the computational graph
          - state():
            returns current state values of lower level variables 
    4. BOMLOpt
       - Aliases: 
           - boml.optimizer.BOMLOpt
       - Methods to be overridden:
           - minimize(loss_inner, var_list=None, global_step=None, gate_gradients=tf.train.Optimizer.GATE_OP,
               aggregation_method=None, colocate_gradients_with_ops=False, name=None, grad_loss=None):
               - Returns: an `bml_inner_grad` object relative to this minimization, same as `tf.train.Optimizer.minimize.`
       - Utility functions:
           - learning_rate():
                 - Returns: the step size of this BOMLOptimizer
       - Utility Functions
           - get_dafault_session():
                get and return the default tensorflow session
       - BatchQueueMock:
        generates batches of taskes and feed them into corresponding placeholders.
  - Utility Modules:
      - get_default_session():
        gets and returns the default tensorflow session
      - BatchQueueMock():
          responsible for generates batches of taskes and feed them into corresponding placeholders.
      - cross_entropy(pred, label):
        return loss function that matches different methods in [ `MetaFeat`, `MetaInit` ]
      - vectorize_all(var_list, name=None):
        Vectorize the variables in the list named var_list with the given name
      - remove_from_collectinon(key,*var_list):
        removes the variables in the var_list according to the given Graph key
      - set_gpu():
        set primary parameters of GPU configuration.
      
## Authors and license<div5 id="a5"></div5>
MIT License

Copyright (c) 2020 Yaohua Liu

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.


