---

title: Semi-supervised deep learning for uterus and bladder segmentation on female
  pelvic floor MRI with limited labeled data.**DOI:** 10.1016/j.ajog.2025.10.004
authors:
- JianweiZuo
- FeiFeng
- ZhuhuiWang
- James AAshton-Miller
- John O LDelancey
- JiajiaLuo
journal: American journal of obstetrics and gynecology
doi: 10.1016/j.ajog.2025.10.004
publication_date: ''
source: Processed from scraped content
processing_date: '2025-10-21T22:15:09.918240'
content_type: research_paper
conditions:
- asd
topics: []
categories:
- asd
reading_level: academic
audience:
- professional
- researcher
patient_friendly: false
search_priority: standard
keywords:
- clinical
search_tags:
- asd
- academic
- peer-reviewed
- research
---



# Semi-supervised deep learning for uterus and bladder segmentation on female pelvic floor MRI with limited labeled data.**DOI:** 10.1016/j.ajog.2025.10.004

# **Authors:** JianweiZuo, FeiFeng, ZhuhuiWang, James AAshton-Miller, John O LDelancey, JiajiaLuo

**Journal:** American journal of obstetrics and gynecology

**DOI:** 10.1016/j.ajog.2025.10.004

## Abstract

## Methods
The aim of this study is to introduce a novel semi-supervised learning process that uses limited data annotation in pelvic MRI to improve automated segmentation. By effectively using both labeled and unlabeled MRI data, our approach seeks to improve the accuracy and efficiency of pelvic organ segmentation, thereby reducing the reliance on extensive labeled datasets for AI model training.
The study used a semi-supervised deep learning framework for uterus and bladder segmentation, in which a model is trained using both a small number of expert-outlined structures and a large number of unlabeled scans, leveraging the information from the labeled data to guide the model and improve its predictions on the unlabeled data. It involved 4,103 MR images from 48 female subjects. This approach included self-supervised learning of image restoration tasks for feature extraction and pseudo-label generation, followed by combined supervised learning on labeled images and unsupervised training on unlabeled images. The method's performance was evaluated quantitatively using the Dice Similarity Coefficient (DSC), Average Surface Distance (ASD), and 95% Hausdorff Distance (HD95). For statistical analysis, two-tailed paired t-tests were conducted for comparison.
This framework demonstrated the capacity to achieve segmentation accuracy comparable to traditional methods while requiring only about 60% of the typically necessary labeled data. Specifically, the semi-supervised approach achieved DSCs of 0.84±0.04, ASDs of 13.98±0.93, HD95s of 2.15±0.40 for the uterus, and 0.92±0.05, 2.51±0.83, 2.88±0.17 for the bladder respectively (P-value<0.001 for all), outperforming both the baseline supervised learning and transfer learning models. Additionally, 3D reconstructions using the semi-supervised method exhibited superior details in the visualized organs.
This study's semi-supervised learning framework wherein the full use of unlabeled data markedly reduces the necessity for extensive manual annotations, achieving high segmentation accuracy with substantially fewer labeled images that can enhance clinical evaluation and advance medical image analysis by reducing the dependency on large-scale labeled pelvic MRI datasets for training.

**Date:** 2025-10-19
**Category:** asd
**Source:** pubmed
**Scraped at:** 2025-10-21T11:05:27.581128
## Methods
The aim of this study is to introduce a novel semi-supervised learning process that uses limited data annotation in pelvic MRI to improve automated segmentation. By effectively using both labeled and unlabeled MRI data, our approach seeks to improve the accuracy and efficiency of pelvic organ segmentation, thereby reducing the reliance on extensive labeled datasets for AI model training.
The study used a semi-supervised deep learning framework for uterus and bladder segmentation, in which a model is trained using both a small number of expert-outlined structures and a large number of unlabeled scans, leveraging the information from the labeled data to guide the model and improve its predictions on the unlabeled data. It involved 4,103 MR images from 48 female subjects. This approach included self-supervised learning of image restoration tasks for feature extraction and pseudo-label generation, followed by combined supervised learning on labeled images and unsupervised training on unlabeled images. The method's performance was evaluated quantitatively using the Dice Similarity Coefficient (DSC), Average Surface Distance (ASD), and 95% Hausdorff Distance (HD95). For statistical analysis, two-tailed paired t-tests were conducted for comparison.
This framework demonstrated the capacity to achieve segmentation accuracy comparable to traditional methods while requiring only about 60% of the typically necessary labeled data. Specifically, the semi-supervised approach achieved DSCs of 0.84±0.04, ASDs of 13.98±0.93, HD95s of 2.15±0.40 for the uterus, and 0.92±0.05, 2.51±0.83, 2.88±0.17 for the bladder respectively (P-value<0.001 for all), outperforming both the baseline supervised learning and transfer learning models. Additionally, 3D reconstructions using the semi-supervised method exhibited superior details in the visualized organs.
## Introduction
*This content was automatically scraped by Webscraping Agent A*